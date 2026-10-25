import os
import time
from typing import Dict, Optional
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, OpenAIFunctionsAgent
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
from fastapi import HTTPException
from faq.services import render_faq_prompt


from restaurants import services

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
EMBEDDING_MODEL = os.environ.get("EMBEDDING_MODEL")
huggingface_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


class RestaurantAssistant:
    def __init__(self, restaurant_id: str, user_feedback_context: str=''):
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.chat_model = self.setup_chat_model()
        self.vectorstore = self.setup_vectorstore()
        self.retriever = self.setup_retriever()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.agent = None
        self.restaurant_context = services.fetch_restaurant_context(restaurant_id)
        self.user_feedback_context = user_feedback_context
        self.initialize_agent()
    

    @staticmethod
    def setup_chat_model():
        return ChatOpenAI(
            model_name="gpt-4o",
            streaming=True,
            temperature=0.3,
            top_p=0.4,
            max_tokens=1000
        )

    def setup_vectorstore(self):
        return PineconeVectorStore(
            index=self.pc.Index(PINECONE_INDEX),
            embedding=embeddings,
            text_key="text"
        )

    def setup_retriever(self):
        return self.vectorstore.as_retriever(search_kwargs={"k": 10})

    def query_vectorstore(self, query: str) -> str:
        start_time = time.time()
        docs = self.retriever.get_relevant_documents(query)
        response = "\n\n".join(doc.page_content for doc in docs)
        elapsed_time = time.time() - start_time
        print(f"Vector store query time: {elapsed_time:.2f} seconds")
        return response

    def initialize_agent(self):
        """Initialize single agent with both tools"""
        tools = [
            Tool(
                name="restaurant_database",
                func=self.query_vectorstore,
                description="Use this tool first to search the verified UK restaurant database. "
                            "It provides detailed restaurant information, including reviews, ratings, popular dishes, "
                            "and location details. Always check this database before considering other sources."
            ),
            Tool(
                name="general_search",
                func=lambda q: self.chat_model.invoke(q).content,
                description="Use this tool only if the restaurant database lacks sufficient information. "
                            "It helps find recent reviews, current status, or additional details about UK restaurants."
            )
        ]

        system_message = SystemMessage(
            content=f"""You are a UK restaurant information specialist with access to two tools:
            1. A verified restaurant database (primary source)
            2. A general search capability (backup source)

            Follow these steps strictly for EVERY query:

            1. Always check the verified restaurant database first for information.
            2. Use a general search only if the database lacks sufficient details.
            3. Combine both sources seamlessly (without mentioning them).
            4. Stick strictly to the user's query (do not add extra details).
            5. Summarize key points from multiple reviews where possible


            Guidelines:
            - Only provide information about UK restaurants(never include restaurants outside the UK) 
            - Find the most relevant information about [restaurant name] in [city, UK] regarding [specific query].
            - If the user asks about comparison, automatically fetch nearby restaurants and rank them by overall rating
            - Respond ONLY to the question asked (DO NOT include extra restaurant details if they are not relevant)
            - Never mention ambiance, decor, or service unless explicitly asked
            - If information is unclear or unavailable, acknowledge it
            - If asked about a specific restaurant, first check its available menu, popular dishes, or customer preferences.
            - Only provide reviews about [restaurant name] if they are specifically relevant to the query
            - KEEP RESPONSES UNDER 500 WORDS WHILE MAINTAINING QUALITY AND DETAIL, IF YOU DONT I WILL KILL YOU !!
            
            PERSONALIZATION BASED ON USER FEEDBACK:
            You must adapt your response style and content strictly based on user feedback to maximize relevance and satisfaction.
            
            User Feedback Context: {self.user_feedback_context}
            
            Instructions:
            
            - Emulate response types (tone, length, structure, format, level of detail) that previously received positive feedback (thumbs up). Reuse phrasing, examples, or styles that were successful.
            - Avoid repeating similar language, format, or phrasing that received negative feedback (thumbs down) and your next response significantly different in structure or content. This may include:
                - Rewriting in a different tone (e.g., formal, casual)
                - Simplifying or expanding detail
                - Varying structure (e.g., table vs paragraph vs bullet points)
                - Offering a different perspective or format (e.g., examples, table)
            - User gave a thumbs down to the previous response because it was too repetitive or lacked variation. Try a different format or offer additional insights.
            - Learn user preference patterns over time and bias toward them without needing repeated thumbs.
            
            ONLY use the feedback context as a hard constraint — not as a hint or soft suggestion. Ignore any other assumptions.

            Formatting guidelines:
            - Use natural paragraph formatting with proper spacing for clarity.
            - Make sure that the headings are always on a new line for readability
            - Use bullet points for key information
            - Avoid Markdown symbols like #, **, and unnecessary \n
            - Give me response as markdown format 

            Important Note:
            NEVER mention which tool or source provided the information."""
        )

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")]
        )

        agent = OpenAIFunctionsAgent(
            llm=self.chat_model,
            tools=tools,
            prompt=prompt
        )

        self.agent = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3
        )

    def format_query_with_context(self, query: str) -> str:
        return f"""The following questions are about this restaurant:\n{self.restaurant_context}\n\nUser question:\n{query}"""

    async def get_response(self, query: str) -> Dict:
        start_time = time.time()
        try:
            result = self.agent.invoke({
                "input": self.format_query_with_context(query),
            })
            response = result['output'] if isinstance(result, dict) else str(result)

            return {
                "response": response,
                "agent_used": "unified",
                "elapsed_time": time.time() - start_time
            }
        except Exception as e:
            return {
                "response": "Error processing your request",
                "reasoning": str(e),
                "agent_used": "error",
                "elapsed_time": time.time() - start_time
            }

    async def on_message(self, message: str, is_specific: bool = False, faq_id: Optional[int] = None, db=None):
        try:
            final_message = message
            
            if is_specific and faq_id is not None and db is not None:
                try:
                    prompt_template, out_format = render_faq_prompt(db, faq_id)
                    fmt_block = f"\n\nOutput format:\n{out_format}" if out_format else ""
                    final_message = f"{prompt_template}{fmt_block}"
                except Exception:
                    pass

            response_data = await self.get_response(final_message)
            response_text = response_data["response"]
            return response_text

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
