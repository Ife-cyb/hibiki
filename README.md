[![Deploy Pipeline](https://github.com/ifeoluwa/Hibiki/actions/workflows/deploy.yml/badge.svg)](https://github.com/ifeoluwa/Hibiki/actions/workflows/deploy.yml)

<div align="center">
  <h1>???? Hibiki</h1>
  <p><strong>A semantic anime search engine powered by vector embeddings.</strong></p>
  <p>Stop searching with exact titles. Start searching by <i>vibes, feelings, and abstract concepts</i>.</p>
  
  <!-- Add your screenshot here later -->
  <img src="https://via.placeholder.com/800x400.png?text=Hibiki+App+Screenshot+Placeholder" alt="Hibiki App Screenshot" style="border-radius: 8px; margin: 20px 0;">
</div>

---

## ??????? Tech Stack

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF5252?style=for-the-badge)
![sentence-transformers](https://img.shields.io/badge/Sentence--Transformers-FF9D00?style=for-the-badge)

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)

![Railway](https://img.shields.io/badge/Railway-131415?style=for-the-badge&logo=railway&logoColor=white)
![Vercel](https://img.shields.io/badge/vercel-%23000000.svg?style=for-the-badge&logo=vercel&logoColor=white)

---

## ???? How It Works

Instead of matching keywords, Hibiki actually understands the *meaning* of your search.

1. **??????????? User Query**: You search for something abstract like *"A sad story about a robot learning to love"*.
2. **???? Embedding**: The backend passes your text through `sentence-transformers` (`all-MiniLM-L6-v2`) to convert it into a multidimensional mathematical vector.
3. **???? Vector Search**: We query the **ChromaDB** database to find anime synopses that sit mathematically closest to your query's vector in the semantic space.
4. **??? Ranked Results**: The API normalizes the distance scores and returns the closest anime matches instantly to the React frontend.

---

## ??????? Architecture & Pipeline

Hibiki is built on a scalable **ETL (Extract, Transform, Load)** and **Semantic Search** architecture:

- **Fetcher (`fetcher.py`)**: Pulls raw anime metadata from GraphQL APIs (AniList) and Kaggle datasets.
- **Cleaner (`cleaner.py`)**: Sanitizes missing data, drops duplicates, and concatenates titles, genres, and synopses into a rich text blob using **Pandas**.
- **Embedder (`embedder.py`)**: Processes the rich text into vector embeddings and loads them into a persistent **ChromaDB** collection.
- **Serving (`main.py`)**: A production-hardened **FastAPI** application exposes the semantic search layer (along with history and caching) to the web.

---

## ???? Getting Started Locally

### 1. Backend (FastAPI & Vector DB)
```bash
# Clone the repository
git clone https://github.com/ifeoluwa/Hibiki.git
cd Hibiki

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install python dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env

# Start the FastAPI server (will auto-populate ChromaDB on first run)
uvicorn backend.main:app --reload --port 8000
```
> **Note:** The API docs will naturally be available at `http://localhost:8000/docs`

### 2. Frontend (React & Vite)
Open a new terminal window:
```bash
# Ensure you are in the project root
npm install

# Start the Vite development server
npm run dev
```
> The frontend will be available at `http://localhost:5173`. Make sure the backend is running!

---

## ???? Deployment

Hibiki is designed to be fully deployable to modern serverless and containerized cloud providers.

- **Frontend (Vercel)**: Configured with client-side routing rewrites (`vercel.json`). Live URL: `https://hibiki.vercel.app` *(placeholder)*
- **Backend (Railway)**: Deployed as a bound Docker container. ChromaDB is configured to bind to a `/data` persistent volume so the vector DB survives ephemeral container reboots safely. API URL: `https://hibiki-api.railway.app` *(placeholder)*

---

## ???? What I Learned

Building Hibiki was a fantastic dive into modern Full-Stack and AI-adjacent development. Key takeaways include:

- **Vector Databases & Ephemeral Cloud Storage**: Learned how to wrangle `ChromaDB` inside cloud containers (Railway) and correctly mount persistent volumes to avoid losing multi-gigabyte generated embeddings on every code deploy.
- **Data Engineering**: Handled massive unnormalized datasets, gracefully resolving missing UI elements and duplicates using Pandas, and formatting data to maximize "semantic matchability".
- **API Security & Hardening**: Implemented production FastAPI standards including strict dynamic CORS mappings, payload limiters to mitigate DoS, and custom token-based dependency injection for admin endpoints.
- **Client-Side Build Optimizations**: Configured Vite base paths and Vercel routing rules to prevent standard React single-page-app "404 on refresh" errors occurring in production.
# hibiki
