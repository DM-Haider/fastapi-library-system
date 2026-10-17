from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# -----------------------
# Sample data (In-memory database)
# -----------------------

books = [
    {"id": 1, "title": "Clean Code", "author": "Robert C. Martin", "publisher": "Prentice Hall"},
    {"id": 2, "title": "The Pragmatic Programmer", "author": "Andrew Hunt", "publisher": "Addison-Wesley"},
    {"id": 3, "title": "Python Crash Course", "author": "Eric Matthes", "publisher": "No Starch Press"},
    {"id": 4, "title": "Deep Work", "author": "Cal Newport", "publisher": "Grand Central Publishing"},
    {"id": 5, "title": "Atomic Habits", "author": "James Clear", "publisher": "Avery"},
]

REQUIRED_FIELDS = ("title", "author", "publisher")


@app.get("/hello/{name}")
async def hello_name(name: str):
    return {"message": f"Hello {name}!"}


@app.get("/hello")
async def hello_query(name: str = "world"):
    return {"message": f"Hello {name}!"}


# -----------------------
# Books endpoints
# -----------------------

@app.get("/books")
async def list_books(query: str | None = None):
    if query is None:
        return {"count": len(books), "results": books}

    query_lower = query.lower()

    filtered_books = [
        book for book in books
        if query_lower in book["title"].lower()
        or query_lower in book["author"].lower()
        or query_lower in book["publisher"].lower()
    ]

    return {
        "query": query,
        "results_count": len(filtered_books),
        "results": filtered_books
    }


@app.get("/books/{book_id}")
async def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(payload: dict):
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required fields: {', '.join(missing)}"
        )

    new_book = {
        "id": max(book["id"] for book in books) + 1,
        "title": payload["title"],
        "author": payload["author"],
        "publisher": payload["publisher"],
    }
    books.append(new_book)
    return new_book


@app.patch("/books/{book_id}")
async def update_book(book_id: int, payload: dict):
    for book in books:
        if book["id"] == book_id:
            for field in REQUIRED_FIELDS:
                if field in payload:
                    book[field] = payload[field]
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for index, book in enumerate(books):
        if book["id"] == book_id:
            books.pop(index)
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")


# -----------------------
# CORS
# -----------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
