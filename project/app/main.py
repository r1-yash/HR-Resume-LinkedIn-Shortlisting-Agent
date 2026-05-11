from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.utils.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI HR Shortlisting Agent - Internship Task 1",
    version="1.0.0",
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware (API Key & Rate Limiting)
# app.add_middleware(SecurityMiddleware)

# Include Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "message": "Welcome to the HR Shortlisting Agent API. Please visit /docs for the API documentation."
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
