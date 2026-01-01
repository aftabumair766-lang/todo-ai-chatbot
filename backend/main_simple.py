"""
Simple FastAPI backend for Phase IV Kubernetes Demo
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Todo AI Chatbot - Phase IV Demo")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Todo AI Chatbot Backend - Phase IV",
        "status": "running",
        "deployment": "Kubernetes (Minikube)",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "backend"}

@app.get("/api/health")
async def api_health():
    return {"status": "ok", "message": "Backend is running in Kubernetes!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
