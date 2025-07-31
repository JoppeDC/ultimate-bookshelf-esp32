import base64
import cv2
import numpy as np
from io import BytesIO
from typing import List, Tuple
from fastapi import HTTPException
import supervision as sv
from inference_sdk import InferenceHTTPClient

from config import settings

class ImageProcessingService:
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=settings.ROBOFLOW_API_URL,
            api_key=settings.ROBOFLOW_API_KEY,
        )
    
    def decode_base64_image(self, base64_image: str) -> np.ndarray:
        try:
            # Remove data URL prefix if present
            if base64_image.startswith('data:image'):
                base64_image = base64_image.split(',')[1]

            image_data = base64.b64decode(base64_image)
            image_array = np.frombuffer(image_data, dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

            if image is None:
                raise ValueError("Could not decode image")

            return image

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid image data: {str(e)}")
    
    def detect_books_in_image(self, image: np.ndarray) -> sv.Detections:
        results = self.client.infer(image, model_id=settings.ROBOFLOW_MODEL_ID)
        return sv.Detections.from_inference(results)
    
    def extract_book_regions(self, image: np.ndarray, detections: sv.Detections) -> Tuple[List[np.ndarray], List]:
        masks_isolated = []
        polygons = [sv.mask_to_polygons(mask) for mask in detections.mask]

        for mask in detections.mask:
            y_indices, x_indices = np.where(mask)
            if len(y_indices) == 0 or len(x_indices) == 0:
                continue

            x_min, x_max = np.min(x_indices), np.max(x_indices)
            y_min, y_max = np.min(y_indices), np.max(y_indices)

            # Extract the region using bounding box
            roi = image[y_min:y_max+1, x_min:x_max+1].copy()

            # Create a mask for the cropped region
            cropped_mask = mask[y_min:y_max+1, x_min:x_max+1]

            # Apply the mask: keep pixels within the polygon, set others to black
            roi[~cropped_mask] = [0, 0, 0]

            masks_isolated.append(roi)

        print("Calculated masks...")

        # Prepare all regions for processing (rotate 90 degrees counterclockwise)
        processed_regions = []
        for region in masks_isolated:
            rotated_region = cv2.rotate(region, cv2.ROTATE_90_COUNTERCLOCKWISE)
            processed_regions.append(rotated_region)

        # Save individual regions for debugging if enabled
        if settings.SAVE_DEBUG_IMAGES:
            for task_id, region in enumerate(processed_regions):
                cv2.imwrite(f"region_{task_id}.jpg", region)
                print(f"Saved clean region_{task_id}.jpg")

        return processed_regions, polygons
    
    def image_to_base64(self, image: np.ndarray) -> str:
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = BytesIO(buffer).read()
        return base64.b64encode(image_bytes).decode('utf-8')
