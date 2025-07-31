from pydantic import BaseModel, Field
from typing import List, Optional

class ImageRequest(BaseModel):
    """Request model for image processing"""
    image: str = Field(..., description="Base64 encoded image data")

class BookAnnotation(BaseModel):
    """Model for a single book annotation"""
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Book author")
    polygons: List[List[List[float]]] = Field(..., description="Polygon coordinates for book detection")
    xyxy: List[float] = Field(..., description="Bounding box coordinates [x1, y1, x2, y2]")

class Shelf(BaseModel):
    """Model for a shelf containing book annotations"""
    shelf_id: int = Field(..., description="Unique identifier for the shelf")
    annotations: List[BookAnnotation] = Field(..., description="List of books on this shelf")

class BookDetectionResponse(BaseModel):
    """Response model for book detection"""
    shelves: List[Shelf] = Field(..., description="List of shelves containing books")
    message: str = Field(default="Books detected successfully", description="Response message")

class ProcessingResult(BaseModel):
    """Model for internal processing results"""
    title: str
    author: str
    def __hash__(self):
        return hash((self.title, self.author))

    def __eq__(self, other):
        if not isinstance(other, ProcessingResult):
            return False
        return self.title == other.title and self.author == other.author

class StatsResponse(BaseModel):
    """Response model for service statistics"""
    total_requests: int = Field(..., description="Total number of detection requests processed")
    total_books_detected: int = Field(..., description="Total number of books detected across all requests")
    total_valid_books: int = Field(..., description="Total number of books with successfully extracted metadata")
    overall_accuracy: float = Field(..., description="Overall accuracy percentage of valid books vs total detected")
    average_books_per_request: float = Field(..., description="Average number of books detected per request")
