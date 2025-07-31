# Ultimate Bookshelf - API

An AI-powered book detection and metadata extraction service built with FastAPI. It uses computer vision to detect books in images and leverages Google Gemini AI to extract book titles and authors from the detected regions.

This project uses [FastAPI](https://fastapi.tiangolo.com/) for the web framework and integrates with [Roboflow](https://roboflow.com/) for object detection and [Google Gemini](https://ai.google.dev/) for AI-powered text extraction.

## ✨ Features

* AI-powered book detection from images using computer vision
* Automatic extraction of book titles and authors using Google Gemini
* Automatic OpenAPI documentation thanks to FastAPI

## 💠 Requirements

* Python 3.8+
* Google Cloud Project with Gemini API access
* Roboflow API key for object detection

## 🔧 Configuration

### Environment Variables

You can set the environment variables in a .env file or directly in the environment. 
You can copy the provided `.env.dist` file to `.env` and fill in your values.


* `ROBOFLOW_API_KEY`: Your Roboflow API key for object detection
* `GOOGLE_CLOUD_PROJECT`: Your Google Cloud project ID
* `GOOGLE_CLOUD_LOCATION`: Google Cloud location (default: "global")
* `DEBUG`: Enable debug mode (default: "False")
* `SAVE_DEBUG_IMAGES`: Save debug images during processing (default: "False")

### `config.py`

Contains all application settings including:
* API endpoints and keys for Roboflow and Google Cloud
* Processing configuration (batch size, max workers)
* Gemini model settings (temperature, max tokens)
* CORS and server configuration

## 🚀 Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   export ROBOFLOW_API_KEY="your_roboflow_api_key"
   export GOOGLE_CLOUD_PROJECT="your_google_cloud_project"
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```
   
---

## 🔍 Processing Pipeline

1. **Image Decoding**: Convert base64 image to OpenCV format
2. **Object Detection**: Use Roboflow model to detect book regions
3. **Region Extraction**: Extract individual book regions from the image
4. **AI Extraction**: Use Google Gemini to extract (aka guess) titles and authors
5. **Annotation Creation**: Combine detection data with extracted metadata
6. **Shelf Grouping**: Group books into shelves based on vertical alignment

---

## 📡 API Endpoints

### `POST /api/v1/detect-books`

Detect books in an image and extract their titles and authors.

#### Request Body

```json
{
  "image": "base64_encoded_image_data"
}
```

* `image`: Base64 encoded image data (required)

#### Response

```json
{
   "shelves": [
      {
         "shelf_id": 1,
         "annotations": [
            {
               "title": "The Great Gatsby",
               "author": "F. Scott Fitzgerald",
               "polygons": [[[100, 50], [300, 50], [300, 200], [100, 200]]],
               "xyxy": [100, 50, 300, 200]
            },
            {
               "title": "To Kill a Mockingbird",
               "author": "Harper Lee",
               "polygons": [[[320, 50], [520, 50], [520, 200], [320, 200]]],
               "xyxy": [320, 50, 520, 200]
            }
         ]
      },
      {
         "shelf_id": 2,
         "annotations": [
            {
               "title": "1984",
               "author": "George Orwell",
               "polygons": [[[100, 250], [300, 250], [300, 400], [100, 400]]],
               "xyxy": [100, 250, 300, 400]
            }
         ]
      }
   ],
   "message": "Successfully detected 3 books across 2 shelves"
}
```

* `shelves`: Array of detected shelves, each containing:
  * `shelf_id`: Unique identifier for the shelf
  * `annotations`: Array of detected books with metadata
    * `title`: Extracted book title
    * `author`: Extracted book author
    * `polygons`: Polygon coordinates for precise book boundaries
    * `xyxy`: Bounding box coordinates [x1, y1, x2, y2]
* `message`: Success message with detection count

### `GET /api/v1/books/stats`

Get some statistics for the service.

#### Response

```json
{
  "total_requests": 42,
  "total_books_detected": 156,
  "total_valid_books": 142,
  "overall_accuracy": 0.9103,
  "average_books_per_request": 3.71
}
```

* `total_requests`: Total number of detection requests processed
* `total_books_detected`: Total number of books detected across all requests
* `total_valid_books`: Total number of books with successfully extracted metadata
* `overall_accuracy`: Overall accuracy percentage of valid books vs total detected
* `average_books_per_request`: Average number of books detected per request

---

## License

MIT
