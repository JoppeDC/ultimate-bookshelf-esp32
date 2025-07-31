from fastapi import APIRouter, HTTPException
from typing import List

from models import ImageRequest, BookDetectionResponse, BookAnnotation, Shelf, StatsResponse
from services import BookDetectionService

router = APIRouter(prefix="/api/v1", tags=["books"])
book_detection_service = BookDetectionService()

@router.post("/detect-books", response_model=BookDetectionResponse)
async def detect_books_endpoint(request: ImageRequest):
    try:
        # Get the flat list of annotations
        annotations = book_detection_service.detect_books_from_base64(request.image)

        # Group them into shelves
        shelves = book_detection_service.group_books_into_shelves(annotations)

        # Flatten annotations from all shelves for statistics
        all_annotations = []
        for shelf in shelves:
            all_annotations.extend(shelf.annotations)

        # Get detection statistics for logging/monitoring
        stats = book_detection_service.get_detection_stats(all_annotations)
        print(f"Detection stats: {stats}")

        total_books = len(all_annotations)
        total_shelves = len(shelves)

        return BookDetectionResponse(
            shelves=shelves,
            message=f"Successfully detected {total_books} books organized into {total_shelves} shelves"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in book detection: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing image: {str(e)}"
        )

@router.get("/books/stats", response_model=StatsResponse)
async def get_books_stats():
    """Get cumulative statistics for book detection service"""
    try:
        stats = book_detection_service.get_cumulative_stats()
        return StatsResponse(**stats)
    except Exception as e:
        print(f"Error retrieving stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )
