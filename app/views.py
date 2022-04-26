from fastapi import Depends, Request, Form
from fastapi.responses import HTMLResponse

from domonic.html import *
from domonic import domonic
from domonic.dom import Node
from domonic.dom import DOMConfig

from app import app, get_db
from app.models import Author, Book

from sqlalchemy.orm import Session


# DOMConfig.GLOBAL_AUTOESCAPE = True # TODO - note a bug on TextNodes when using parsed html...
DOMConfig.HTMX_ENABLED = True

# template for book row
book_row_tmpl = lambda author, title, id: tr(
                    td(title), td(author),
                    td(button("Edit Title", _class="btn btn-primary", _get=f"/get-edit-form/{id}",)),
                    td(button("Delete", _class="btn btn-warning", _delete=f"/delete/{id}",)),
                )


@app.get("/")
def home(the_sesh: Session = Depends(get_db)):
    mydom = domonic.parseString(
    '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>FAST-API HTMX ALPINE App</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet"
            integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">
        <link href="/static/css/styles.css" rel="stylesheet">
        <!-- HTMX -->
        <script src="https://unpkg.com/htmx.org@1.5.0"></script>
    </head>
    <body>
        <h1>Book Recommendations</h1>
        <form hx-post="/submit" hx-swap="beforeend" hx-target="#new-book" class="mb-3">
            <input type="text" placeholder="Book Title" name="title" class="form-control mb-3" />
            <input type="text" placeholder="Book Author" name="author" class="form-control mb-3" />
            <button type="submit" class="btn btn-primary">Submit</button>
        </form>
        <table class="table">
            <thead>
              <tr>
                <th scope="col">Book Title</th>
                <th scope="col">Book Author</th>
              </tr>
            </thead>
            <tbody id="new-book" hx-target="closest tr" hx-swap="outerHTML swap:0.5s"></tbody>
        </table>
    </body>
    </html>
    ''')

    target = mydom.querySelector('#new-book')
    # print(str(mydom))
    books = the_sesh.query(Book).all()
    for book in books:
        author = the_sesh.query(Author).where(Author.id == book.author_id).first()
        target += book_row_tmpl(author.name, book.title, book.id)

    # print(mydom.__pyml__())
    return HTMLResponse(f"{mydom}")
    # return HTMLResponse(str(mydom))


@app.get("/get-book-row/{id}")
def get_book_row(id, the_sesh: Session = Depends(get_db)):
    book = the_sesh.query(Book).where(Book.id == id).first()
    author = the_sesh.query(Author).where(Author.id == book.author_id).first()
    response = book_row_tmpl(author.name, book.title, id)
    return HTMLResponse(str(response))


@app.get("/get-edit-form/{id}")
def get_edit_form(id, the_sesh: Session = Depends(get_db)):
    book = the_sesh.query(Book).where(Book.id == id).first()
    author = the_sesh.query(Author).where(Author.id == book.author_id).first()

    response = f"""
    <tr hx-trigger='cancel' class='editing' hx-get="/get-book-row/{id}">
      <td><input name="title" value="{book.title}"/></td>
      <td>{author.name}</td>
      <td>
        <button class="btn btn-primary" hx-get="/get-book-row/{id}">
          Cancel
        </button>
        </td>
        <td>
        <button class="btn btn-primary" hx-put="/update/{id}" hx-include="closest tr">
          Save
        </button>
      </td>
    </tr>
    """
    # response = book_row_tmpl(book.title, author.name , id)
    # response.className = 'editing'
    # response.setAttribute( 'hx-trigger', 'cancel')
    # response.setAttribute( 'hx-get', f"/get-book-row/{id}")
    return HTMLResponse(str(response))


@app.put("/update/{id}")
def update_book(id, title: str = Form(...), the_sesh: Session = Depends(get_db)):
    the_sesh.query(Book).filter(Book.id == id).update({"title": title})
    the_sesh.commit()
    book = the_sesh.query(Book).where(Book.id == id).first()
    author = the_sesh.query(Author).where(Author.id == book.author_id).first()
    response = book_row_tmpl(author.name, book.title, id)
    return HTMLResponse(str(response))


@app.delete("/delete/{id}")
def delete_book(id, the_sesh: Session = Depends(get_db)):
    book = the_sesh.query(Book).where(Book.id == id).first()
    the_sesh.delete(book)
    the_sesh.commit()
    return HTMLResponse("")


@app.post('/submit')
def submit(title: str = Form(...), author: str = Form(...), the_sesh: Session = Depends(get_db)):
    author_exists = the_sesh.query(Author).filter(Author.name == author).first()
    # print("THE AUTHOR::", author_exists)
    if author_exists:
        author_id = author_exists.id
        book = Book(author_id=author_id, title=title)
        the_sesh.add(book)
        the_sesh.commit()
    else:
        author = Author(name=author)
        the_sesh.add(author)
        the_sesh.commit()

        book = Book(author_id=author.id, title=title)
        the_sesh.add(book)
        the_sesh.commit()

    response = book_row_tmpl(author, title, id)
    return HTMLResponse(str(response))
