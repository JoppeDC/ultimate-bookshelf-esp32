from .books import router as books_router
from .index import router as index_router

__all__ = [
    "books_router",
    "index_router"
]
