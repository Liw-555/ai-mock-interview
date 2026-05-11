"""
FastAPI entry point for Interview Agent MVP.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.database import init_db
from routers import resume, interview, report, question, profile, voice, reflection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown


app = FastAPI(
    title="Interview Agent API",
    description="AI 模拟面试系统后端 API",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(resume.router, prefix="/api/resumes", tags=["简历管理"])
app.include_router(profile.router, prefix="/api/profiles", tags=["岗位资料"])
app.include_router(interview.router, prefix="/api/sessions", tags=["面试会话"])
app.include_router(report.router, prefix="/api/sessions", tags=["评估报告"])
app.include_router(question.router, prefix="/api/questions", tags=["面试问题"])
app.include_router(voice.router, prefix="/api/voice", tags=["语音"])
app.include_router(reflection.router, prefix="/api/sessions", tags=["反思总结"])


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "Interview Agent API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
