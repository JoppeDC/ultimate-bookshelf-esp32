import base64
import json
import re
from io import BytesIO
from typing import List
import cv2
import numpy as np
from google import genai
from google.genai import types

from config import settings
from models import ProcessingResult

class GeminiService:
    def __init__(self):
        self.client = genai.Client(
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT,
            location=settings.GOOGLE_CLOUD_LOCATION,
        )
        
        self.system_instruction = (
            "You are an expert bibliographic AI specialized in analyzing images of books and book spines."
            "Each provided image will contain one or multiple books."
            "For every image provided, identify exactly one prominent book. If a book's title or author is not clearly visible, explicitly return 'Title Unknown' and/or 'Author Unknown' accordingly."
            "Return your results in structured JSON, with exactly one entry per input image, preserving the exact input order."
        )

        self.text_prompt = (
            "Analyze each of the following images, identifying exactly one prominent book per image."
            "Provide the book's title and author only if clearly readable from the spine or cover."
            "\n"
            "If the title or author is unclear or unreadable, use 'Title Unknown' or 'Author Unknown' accordingly."
            "\n\n"
            "Output your response as structured JSON, maintaining the exact order of the images provided."
        )
    
    def _prepare_image_parts(self, regions: List[np.ndarray]) -> List[types.Part]:
        image_parts = []
        for region in regions:
            base64_image = base64.b64encode(
                BytesIO(cv2.imencode(".jpg", region)[1]).read()
            ).decode("utf-8")

            image_part = types.Part.from_bytes(
                data=base64.b64decode(base64_image),
                mime_type="image/jpeg",
            )
            image_parts.append(image_part)
        
        return image_parts
    
    def _create_generation_config(self) -> types.GenerateContentConfig:
        return types.GenerateContentConfig(
            temperature=settings.GEMINI_TEMPERATURE,
            thinking_config=types.ThinkingConfig(thinking_budget=-1),
            max_output_tokens=settings.GEMINI_MAX_OUTPUT_TOKENS,
            system_instruction=[types.Part.from_text(text=self.system_instruction)],
            response_mime_type="application/json",
            response_schema={
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "title": {"type": "STRING"},
                        "author": {"type": "STRING"}
                    },
                    "required": ["title", "author"]
                }
            },
        )
    
    def _parse_gemini_response(self, response, num_regions: int) -> List[ProcessingResult]:
        try:
            # Extract response text
            if hasattr(response, 'text'):
                response_text = response.text
            else:
                response_text = str(response)

            # Parse JSON response
            try:
                books_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response using regex
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    books_data = json.loads(json_match.group(0))
                else:
                    raise ValueError("Could not extract JSON from response")

            # Process each book in the response
            results = []
            for i in range(num_regions):
                if i < len(books_data):
                    book = books_data[i]
                    if isinstance(book, dict):
                        title = book.get("title", "Title Unknown")
                        author = book.get("author", "Author Unknown")
                    else:
                        title = "Title Unknown"
                        author = "Author Unknown"
                else:
                    title = "Title Unknown"
                    author = "Author Unknown"

                result = ProcessingResult(
                    title=title,
                    author=author
                )
                results.append(result)

            return results

        except Exception as e:
            print(f"Error parsing response: {e}")
            if hasattr(response, 'text'):
                print(f"Response: {response.text}")
            else:
                print(f"Response: {response}")
            
            # Return default results for all regions
            return [
                ProcessingResult(title="Title Unknown", author="Author Unknown")
                for _ in range(num_regions)
            ]
    
    def process_book_regions(self, regions: List[np.ndarray]) -> List[ProcessingResult]:
        print(f"Processing {len(regions)} masks with Gemini...")

        # Prepare image parts for Gemini
        image_parts = self._prepare_image_parts(regions)

        # Create text part
        text_part = types.Part.from_text(text=self.text_prompt)

        # Create generation config
        config = self._create_generation_config()
        
        # Create content for the request
        parts = image_parts + [text_part]
        contents = [
            types.Content(
                role="user",
                parts=parts
            ),
        ]

        # Make request to Gemini
        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=contents,
            config=config,
        )

        # Parse response and convert to formatted strings
        processing_results = self._parse_gemini_response(response, len(regions))
        
        return processing_results
