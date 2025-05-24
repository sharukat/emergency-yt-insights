# AI-Driven Emergency Insight Platform from Crowd-Sourced Video Data 

This is an AI-powered platform that leverages crowd-sourced YouTube content to extract, analyze, and generate real-time insights during emergency events. By processing transcripts from relevant videos, it enables rapid decision-making, planning, and situational awareness using cutting-edge NLP techniques, vector search, and a conversational AI assistant.

## 🌱 Motivation
In the wake of global emergencies—natural disasters, conflicts, or crises—people turn to platforms like YouTube to share videos, documentaries, interviews, and personal experiences. These user-generated resources are rich with real-time information, yet underutilized. This application taps into this untapped data, transforming crowd-sourced content into actionable insights using semantic filtering, vector-based retrieval, sentiment analysis, and topic modeling—empowering emergency response teams and analysts with critical, timely knowledge.

## 🚀 Getting Started
### Frontend
1. **Navigate to the frontend directory and install dependencies using the provided package-lock.toml.**
   ```bash
   cd frontend
   npm install
   ```
2. **Build and run the development server.**
   ```bash
   npm run build
   npm start
   ```
### Backend
1. **Ensure Docker and Docker Compose are installed.**
2. **Run the backend services using Docker Compose.**
   ```bash
   docker-compose up --build
   ```
   This will start:
   - The backend service (Flask/FastAPI)
   - MongoDB (for storing metadata and sentiment/topic analysis)
   - Qdrant (for vector storage of chunked transcripts)
   - Ollama (for embeddings and LLM responses)
3. Before running the backend, ensure:
   - The Ollama container has the Nomic embedding model downloaded.
   - A Groq API Key is available for chat model inference.
  
## 💻 Technology Stack
<p align="center">
  <a href="https://go-skill-icons.vercel.app/">
    <img
      src="https://go-skill-icons.vercel.app/api/icons?i=python,typescript,fastapi,nextjs,tailwindcss,docker,langchain,ollama,groq,youtube"
    />
  </a>
</p>
