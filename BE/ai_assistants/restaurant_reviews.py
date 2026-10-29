import asyncio
import os
import time
from typing import Dict, List, Optional
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from fastapi import HTTPException
from faq.services import render_faq_prompt


from restaurants import services

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
huggingface_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN")

# Prefer the model bundled in the repo (local_models/) over a Hub download:
# on free-tier hosts the first-boot download can take long enough to blow
# past the platform's port-detection deadline, which looks like a silent hang.
_LOCAL_EMBEDDING_MODEL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "local_models", "all-MiniLM-L6-v2",
)
EMBEDDING_MODEL = (
    _LOCAL_EMBEDDING_MODEL
    if os.path.isdir(_LOCAL_EMBEDDING_MODEL)
    else os.environ.get("EMBEDDING_MODEL")
)

_embeddings = None


def get_embeddings():
    """Load the embedding model lazily, on first real use, rather than at
    import time. Importing/loading it eagerly means it runs during `uvicorn`
    startup, before the app has bound to its port — on a resource-constrained
    host that can be slow enough to blow past the platform's port-detection
    deadline, which looks like a silent hang with no error anywhere."""
    global _embeddings
    if _embeddings is None:
        from langchain_huggingface import HuggingFaceEmbeddings
        _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return _embeddings


_vectorstore = None


def get_vectorstore() -> PineconeVectorStore:
    """Build the Pinecone client/index/vectorstore once and reuse it for every
    message. These used to be rebuilt from scratch per chat message, each
    paying for a fresh Pinecone connection on top of blocking the single
    request-handling thread for the duration."""
    global _vectorstore
    if _vectorstore is None:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        _vectorstore = PineconeVectorStore(
            index=pc.Index(PINECONE_INDEX),
            embedding=get_embeddings(),
            text_key="text",
        )
    return _vectorstore


class RestaurantAssistant:
    def __init__(self, restaurant_id: str, user_feedback_context: str='', history: Optional[List[Dict]] = None):
        self.chat_model = self.setup_chat_model()
        self.vectorstore = get_vectorstore()
        self.restaurant_context = services.fetch_restaurant_context(restaurant_id)
        self.restaurant_name = self._extract_restaurant_name(self.restaurant_context)
        self.retriever = self.setup_retriever()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self.load_history(history or [])
        self.user_feedback_context = user_feedback_context
        self.system_message = self.build_system_message()

    @staticmethod
    def _extract_restaurant_name(restaurant_context: str) -> Optional[str]:
        for line in restaurant_context.splitlines():
            if line.startswith("Restaurant Name:"):
                return line.split(":", 1)[1].strip()
        return None
    

    @staticmethod
    def setup_chat_model():
        return ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            temperature=0.3,
            top_p=0.4,
            max_output_tokens=1000
        )

    def load_history(self, history: List[Dict]):
        """Load earlier messages of this conversation so follow-up questions have context"""
        for entry in history:
            if entry.get("author") == "user":
                self.memory.chat_memory.add_user_message(entry["content"])
            else:
                self.memory.chat_memory.add_ai_message(entry["content"])

    def setup_retriever(self):
        # Without this filter, retrieval searches the whole Pinecone index —
        # which also holds the onboarded competitors — so results bleed
        # across restaurants. Scope every search to this restaurant only.
        search_kwargs = {"k": 10}
        if self.restaurant_name:
            search_kwargs["filter"] = {"restaurant_name": self.restaurant_name}
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def query_vectorstore(self, query: str) -> str:
        start_time = time.time()
        docs = self.retriever.get_relevant_documents(query)
        response = "\n\n".join(doc.page_content for doc in docs)
        elapsed_time = time.time() - start_time
        print(f"Vector store query time: {elapsed_time:.2f} seconds")
        return response

    def build_system_message(self) -> SystemMessage:
        """Build the system prompt. Retrieval always runs first (in get_response),
        so the model is simply given the retrieved context plus its own general
        knowledge as a fallback — no agentic tool-calling required."""
        return SystemMessage(
            content=f"""You are a restaurant information specialist. For every query you are given:
            1. Context retrieved from a verified restaurant database (primary source)
            2. Your own general knowledge (backup source, used only if the database context is insufficient)

            Follow these steps strictly for EVERY query:

            1. Always rely on the verified restaurant database context first.
            2. Fall back on general knowledge only if that context lacks sufficient details.
            3. Combine both sources seamlessly (without mentioning them).
            4. Stick strictly to the user's query (do not add extra details).
            5. Summarize key points from multiple reviews where possible


            Guidelines:
            - Only provide information about restaurants that are present in the verified restaurant database for this conversation.
            - Find the most relevant information about [restaurant name] in [city] regarding [specific query].
            - If the user asks about comparison, automatically fetch nearby restaurants and rank them by overall rating
            - Respond ONLY to the question asked (DO NOT include extra restaurant details if they are not relevant)
            - Never mention ambiance, decor, or service unless explicitly asked
            - If information is unclear or unavailable, acknowledge it
            - If asked about a specific restaurant, first check its available menu, popular dishes, or customer preferences.
            - Only provide reviews about [restaurant name] if they are specifically relevant to the query
            - Keep responses under 500 words while maintaining quality and detail.
            
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
            - Learn user preference patterns over time and bias toward them without needing repeated thumbs.
            
            ONLY use the feedback context as a hard constraint — not as a hint or soft suggestion. Ignore any other assumptions.

            Formatting guidelines:
            - Use natural paragraph formatting with proper spacing for clarity.
            - Make sure that the headings are always on a new line for readability
            - Use bullet points for key information
            - Format the response as Markdown, avoiding unnecessary blank lines

            Important Note:
            NEVER mention which source provided the information."""
        )

    def format_query_with_context(self, query: str) -> str:
        return f"""The following questions are about this restaurant:\n{self.restaurant_context}\n\nUser question:\n{query}"""

    async def get_response(self, query: str) -> Dict:
        start_time = time.time()
        # Errors propagate so the caller can report them (and not charge the user for a message).
        # query_vectorstore is a blocking network call to Pinecone; run it off the event
        # loop thread so it doesn't freeze every other in-flight request on this process.
        retrieved_context = await asyncio.to_thread(self.query_vectorstore, query)
        human_content = (
            f"Verified restaurant database context:\n{retrieved_context or '(no matching results found)'}"
            f"\n\n{self.format_query_with_context(query)}"
        )
        messages = (
            [self.system_message]
            + list(self.memory.chat_memory.messages)
            + [HumanMessage(content=human_content)]
        )
        ai_message = await self.chat_model.ainvoke(messages)
        response = ai_message.content

        self.memory.chat_memory.add_user_message(query)
        self.memory.chat_memory.add_ai_message(response)

        return {
            "response": response,
            "agent_used": "unified",
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
