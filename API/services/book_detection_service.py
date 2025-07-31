from typing import List, Optional, Dict, Any
import numpy as np

from config import settings
from models import BookAnnotation, Shelf
from .image_service import ImageProcessingService
from .gemini_service import GeminiService

class BookDetectionService:
    """Main service that orchestrates the book detection pipeline"""

    def __init__(self):
        self.image_service = ImageProcessingService()
        self.gemini_service = GeminiService()
        # Initialize cumulative stats tracking
        self._total_requests = 0
        self._total_books_detected = 0
        self._total_valid_books = 0

    def _get_book_vertical_info(self, book: BookAnnotation) -> Optional[Dict[str, float]]:
        if not book.xyxy or len(book.xyxy) != 4:
            return None

        x1, y1, x2, y2 = book.xyxy
        center_y = (y1 + y2) / 2

        return {
            "centerY": center_y,
            "top": y1,
            "bottom": y2
        }

    def _should_be_on_same_shelf(self, book1_info: Dict[str, float], book2_info: Dict[str, float]) -> bool:
        if not book1_info or not book2_info:
            return False

        # Check for vertical overlap
        overlap_top = max(book1_info["top"], book2_info["top"])
        overlap_bottom = min(book1_info["bottom"], book2_info["bottom"])

        # If there's any vertical overlap, they should be on the same shelf
        return overlap_top < overlap_bottom

    def group_books_into_shelves(self, books: List[BookAnnotation]) -> List[Shelf]:
        if not books:
            return []

        # Get book info and sort by vertical position
        book_infos = []
        for book in books:
            info = self._get_book_vertical_info(book)
            if info is not None:
                book_infos.append({"book": book, "info": info})

        if not book_infos:
            return []

        # Sort by vertical center position
        book_infos.sort(key=lambda x: x["info"]["centerY"])

        shelves = []
        current_shelf = [book_infos[0]["book"]]
        shelf_counter = 1

        # Single pass grouping
        for i in range(1, len(book_infos)):
            current_book = book_infos[i]
            last_book_in_shelf = current_shelf[-1]
            last_book_info = self._get_book_vertical_info(last_book_in_shelf)

            if self._should_be_on_same_shelf(last_book_info, current_book["info"]):
                current_shelf.append(current_book["book"])
            else:
                shelves.append(Shelf(shelf_id=shelf_counter, annotations=current_shelf))
                current_shelf = [current_book["book"]]
                shelf_counter += 1

        # Add the last shelf
        shelves.append(Shelf(shelf_id=shelf_counter, annotations=current_shelf))
        return shelves

    def detect_books_from_base64(self, base64_image: str) -> List[BookAnnotation]:
        image = self.image_service.decode_base64_image(base64_image)
        detections = self.image_service.detect_books_in_image(image)

        # Extract book regions from detections
        processed_regions, polygons = self.image_service.extract_book_regions(image, detections)

        if not processed_regions:
            return []

        # Process regions in batches using Gemini
        books = []
        batch_size = settings.BATCH_SIZE

        for i in range(0, len(processed_regions), batch_size):
            batch = processed_regions[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1} with {len(batch)} regions...")
            batch_results = self.gemini_service.process_book_regions(batch)
            books.extend(batch_results)

        print("Processed books...")

        # Create annotations using only Gemini results
        annotations = self._create_annotations(
            books=books,
            polygons=polygons,
            detections=detections
        )

        # Update cumulative stats
        self._update_cumulative_stats(annotations)

        return annotations

    def _create_annotations(
        self,
        books: List[str],
        polygons: List,
        detections
    ) -> List[BookAnnotation]:
        annotations = []

        for i, (book, polygon_list, xyxy) in enumerate(
            zip(books, polygons, detections.xyxy)
        ):
            # Use only Gemini results
            print(f"Processing book {i+1}: {book}")
            title = book.title
            author = book.author

            print(f"Title: {title}, Author: {author}")

            annotation = BookAnnotation(
                title=title,
                author=author,
                polygons=[polygon.tolist() for polygon in polygon_list],
                xyxy=xyxy.tolist(),
            )
            annotations.append(annotation)

        return annotations

    def get_detection_stats(self, annotations: List[BookAnnotation]) -> dict:
        total_books = len(annotations)

        # If title or author contain the word "Unknown", we consider it as not detected
        valid_books = sum(1 for book in annotations if book.title != "Title Unknown" and book.author != "Author Unknown")

        return {
            "total_books_detected": total_books,
            "valid_books": valid_books,
            "accuracy": valid_books / total_books if total_books > 0 else 0.0
        }

    def _update_cumulative_stats(self, annotations: List[BookAnnotation]) -> None:
        """Update cumulative statistics with data from the current detection request"""
        self._total_requests += 1
        total_books = len(annotations)
        valid_books = sum(1 for book in annotations if book.title != "Title Unknown" and book.author != "Author Unknown")

        self._total_books_detected += total_books
        self._total_valid_books += valid_books

    def get_cumulative_stats(self) -> dict:
        """Get cumulative statistics across all detection requests"""
        overall_accuracy = (self._total_valid_books / self._total_books_detected) if self._total_books_detected > 0 else 0.0
        average_books_per_request = (self._total_books_detected / self._total_requests) if self._total_requests > 0 else 0.0

        return {
            "total_requests": self._total_requests,
            "total_books_detected": self._total_books_detected,
            "total_valid_books": self._total_valid_books,
            "overall_accuracy": round(overall_accuracy, 4),
            "average_books_per_request": round(average_books_per_request, 2)
        }
