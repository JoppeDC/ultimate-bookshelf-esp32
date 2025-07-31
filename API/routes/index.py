from fastapi import APIRouter

router = APIRouter(tags=["index"])

@router.get("/")
async def root():
    return {
        "name": "Ultimate Bookshelf API",
        "description": "AI-powered book detection and metadata extraction service",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "detect_books": "/api/v1/detect-books",
            "service_stats": "/api/v1/books/stats"
        }
    }
