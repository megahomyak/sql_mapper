from sql_mapper import ModelBase
from sql_mapper.sql_executors import SQLiteSQLExecutor


class Book(ModelBase):
    _tablename = "books"
    id: int = "INTEGER"
    title: str = "TEXT"
    _additional_table_lines = "PRIMARY KEY (id)"


class Author(ModelBase):
    _tablename = "authors"
    id: int = "INTEGER"
    name: str = "TEXT"
    _additional_table_lines = "PRIMARY KEY (id)"


class BookToAuthor(ModelBase):
    _tablename = "books_to_authors"
    book_id: int = "INTEGER"
    author_id: int = "INTEGER"
    _additional_table_lines = (
        "FOREIGN KEY (book_id) REFERENCES books(id),"
        "FOREIGN KEY (author_id) REFERENCES authors(id)"
    )


class BookNameAndAuthorName(ModelBase):
    book_title: str
    author_name: str


def test_example_from_docs():
    sql_executor = SQLiteSQLExecutor.new(":memory:")
    sql_executor.create_tables(Book, Author, BookToAuthor)
    for author_name, book_names in (
        ("Michael Z.", ("My Great Book", "My Another Great Book")),
        ("Anna S.", ("BOOK 1", "BOOK 2"))
    ):
        book_ids = []
        for book_title in book_names:
            sql_executor.execute(
                "INSERT INTO ?", [Book(title=book_title)]
            )
            book_ids.append(sql_executor.cursor.lastrowid)
        sql_executor.execute(
            "INSERT INTO ?", [Author(name=author_name)]
        )
        author_id = sql_executor.cursor.lastrowid
        sql_executor.execute_many(
            "INSERT INTO ?", [
                [BookToAuthor(book_id, author_id)]
                for book_id in book_ids
            ]
        )
    sql_executor.commit()
    assert list(sql_executor.execute(
        "SELECT books.title, authors.name FROM books "
        "INNER JOIN books_to_authors ON books_to_authors.book_id = books.id "
        "INNER JOIN authors ON authors.id = books_to_authors.author_id",
        model=BookNameAndAuthorName
    )) == [
        BookNameAndAuthorName("My Great Book", "Michael Z."),
        BookNameAndAuthorName("My Another Great Book", "Michael Z."),
        BookNameAndAuthorName("BOOK 1", "Anna S."),
        BookNameAndAuthorName("BOOK 2", "Anna S.")
    ]
