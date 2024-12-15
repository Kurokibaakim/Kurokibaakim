# Тестовое ТЗ

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date

DATABASE_URL = "postgresql://user:password@localhost/library_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Author(Base):
    __tablename__ = "authors"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    birth_date = Column(Date)


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    author_id = Column(Integer, ForeignKey('authors.id'))
    available_copies = Column(Integer)

    author = relationship("Author")


class Borrow(Base):
    __tablename__ = "borrows"
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey('books.id'))
    reader_name = Column(String)
    borrow_date = Column(Date)
    return_date = Column(Date, nullable=True)

    book = relationship("Book")


Base.metadata.create_all(bind=engine)


class AuthorCreate(BaseModel):
    first_name: str
    last_name: str
    birth_date: date


class BookCreate(BaseModel):
    title: str
    description: str
    author_id: int
    available_copies: int


class BorrowCreate(BaseModel):
    book_id: int
    reader_name: str
    borrow_date: date


app = FastAPI()


@app.post("/authors")
def create_author(author: AuthorCreate):
    db = SessionLocal()
    db_author = Author(**author.dict())
    db.add(db_author)
    db.commit()
    db.refresh(db_author)
    db.close()
    return db_author


@app.get("/authors")
def get_authors():
    db = SessionLocal()
    authors = db.query(Author).all()
    db.close()
    return authors


@app.post("/books")
def create_book(book: BookCreate):
    db = SessionLocal()
    db_book = Book(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    db.close()
    return db_book


@app.get("/books")
def get_books():
    db = SessionLocal()
    books = db.query(Book).all()
    db.close()
    return books

@app.post("/borrows")
def create_borrow(borrow: BorrowCreate):
    db = SessionLocal()
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if book is None or book.available_copies <= 0:
        db.close()
        raise HTTPException(status_code=400, detail="Книга недоступна для выдачи.")

    db_borrow = Borrow(**borrow.dict())
    book.available_copies -= 1
    db.add(db_borrow)
    db.commit()
    db.refresh(db_borrow)
    db.close()
    return db_borrow


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
