# 🥡 Review Munch - API

## 📖 Description  
**Review Munch** is an AI-powered restaurant review and recommendation system that uses Retrieval-Augmented Generation (RAG) to answer user queries related to restaurant food, ambiance, service, cuisine types, and more.  

It includes the application API endpoints with user authentication, vector-based semantic search, analytics dashboard, and settings management.

---

## 🛠️ Tech Stack
- **Backend:** [FastAPI](https://fastapi.tiangolo.com/), [LangChain](https://www.langchain.com/)  
- **LLM:** OpenAI (RAG-powered)
- **Vector Store:** Pinecone  
- **Authentication:** JWT-based Auth  
- **Deployment:** Docker, Docker Compose  

---

## 🚀 Features
- 🔐 User Authentication (Signup, Login, Forgot/Reset Password)
- 💬 AI Chatbot (RAG-based Q&A on restaurant reviews)
- 📊 Dashboard with restaurant insights and analytics
- 🛠️ Settings panel (Update password and user profile)
- 🌍 Scraped reviews used to generate meaningful and contextual responses using LLMs
- 🐳 Containerized with Docker for smooth deployment

---

## 🏗️ Backend Setup (FastAPI)
1. **Clone the repository**
   ```bash
   git clone https://github.com/hamza-shafiq/review-munch-agent
   cd review-munch-agent
   ```

2. **Create & Activate Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file based on the example:

   ```bash
   cp .env.example .env
   ```

   Update values like:
   - `OPENAI_API_KEY=...`
   - `PINECONE_API_KEY=...`
   - `JWT_SECRET_KEY=...`

5. **Run the App**
   ```bash
   uvicorn app:app --reload
   ```
---

## 🐳 Docker Deployment

1. **Ensure Docker and Docker Compose are installed**

2. **Run backend with one command**
   ```bash
   docker-compose up --build
   ```

   - FastAPI backend will be available at: `http://localhost:8000`

---

## 📎 Links

- **Frontend Repository:** [Next.js Dashboard](https://github.com/hamza-shafiq/review-munch-dashboard)  
- **Backend Repository:** [FastAPI + LLM Agent](https://github.com/hamza-shafiq/review-munch-agent)  
- **Live App:** [http://reviewmunch.com](http://reviewmunch.com)
