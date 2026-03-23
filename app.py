from flask import Flask, request, render_template, redirect, url_for
import os
from data_models import db, Author, Book
from datetime import datetime

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


def parse_date(value):
  if not value:
    return None
  try:
    return datetime.strptime(value, '%Y-%m-%d').date()
  except ValueError:
    return 'invalid'


def book_author_query():
  return db.session.query(Book, Author).join(Author, Book.author_id == Author.id)


@app.route('/')
def home():
  books = book_author_query().all()
  return render_template('home.html', books=books)


@app.route('/sort_by_title', methods=['POST'])
def sort_title():
  books = book_author_query().order_by(Book.title).all()
  return render_template('home.html', books=books)



@app.route('/sort_by_author', methods=['POST'])
def sort_author():
  books = book_author_query().order_by(Author.name).all()
  return render_template('home.html', books=books)


@app.route('/search', methods=['POST'])
def search():
  to_find = request.form.get('search')
  if not to_find or not to_find.strip():
      return render_template('search.html', msg="Please enter a search term.")

  books = book_author_query().filter(Book.title.contains(to_find)).all()

  if not books:
    return render_template("search.html", msg="no books found")
  return render_template('search.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
  if request.method == 'GET':
    return render_template('add_author.html')
  add_name = request.form.get('name', '')
  if not add_name.strip():
    return render_template('add_author.html', msg="Author name is required.")

  add_birth_date = parse_date(request.form.get('birthdate'))
  add_date_of_death = parse_date(request.form.get('date_of_death'))
  if 'invalid' in (add_birth_date, add_date_of_death):
    return render_template('add_author.html', msg="Dates must be in YYYY-MM-DD format.")


  author = Author(
    name = add_name,
    birth_date = add_birth_date,
    date_of_death = add_date_of_death
  )
  try:
    db.session.add(author)
    db.session.commit()
    msg = f'The author {add_name} has been added successfully!'
    return render_template('add_author.html', msg=msg)
  except Exception:
    db.session.rollback()
    return render_template('add_author.html', msg="Database error. Please try again.")


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
  authors = db.session.query(Author) \
    .all()
  if request.method == 'GET':
    return render_template('add_book.html', authors=authors)
  add_isbn = request.form.get('isbn', '').strip()
  add_title = request.form.get('title', '').strip()
  add_publication_year = request.form.get('publication_year')
  if add_publication_year:
    try:
      add_publication_year = int(add_publication_year)
      if not (1000 <= add_publication_year <= 2026):
        raise ValueError
    except ValueError:
      return render_template('add_book.html', authors=authors, msg="Enter a valid publication year.")
  add_cover = request.form.get('cover')
  add_author_id = request.form.get('authors')
  if not add_isbn or not add_title or not add_author_id:
    return render_template('add_book.html', authors=authors, msg="ISBN, title, and author are required.")

  if add_author_id and not db.session.get(Author, add_author_id):
    return render_template('add_book.html', authors=authors, msg="Selected author does not exist.")


  existing = db.session.query(Book).filter_by(isbn=add_isbn).first()
  if existing:
      return render_template('add_book.html', authors=authors, msg="A book with that ISBN already exists.")

  book = Book(
    isbn = add_isbn,
    title = add_title,
    publication_year = add_publication_year,
    author_id = add_author_id,
    cover = add_cover
  )
  try:
    db.session.add(book)
    db.session.commit()
    msg = f"The book {add_title} has been added successfully"
    return render_template('add_book.html', authors=authors, msg=msg)
  except Exception:
    db.session.rollback()
    return render_template('add_book.html', msg='Database error. Please try again.')


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
  try:
    book = db.session.get(Book, book_id)
    if not book:
      return redirect(url_for('home'))
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('home'))
  except Exception:
    db.session.rollback()
    return render_template('home.html', msg='Database error. Please try again.')



@app.route('/authors')
def view_authors():
  authors = db.session.query(Author) \
    .all()
  return render_template('authors.html', authors=authors)



@app.route('/authors/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
  try:
    author = db.session.get(Author, author_id)
    if not author:
      return redirect(url_for('view_authors'))
    has_books = db.session.query(Book).filter_by(author_id=author_id).first()
    if has_books:
      authors = db.session.query(Author).all()
      return render_template('authors.html', authors=authors, msg="Cannot delete an author who has books.")
    db.session.delete(author)
    db.session.commit()
    authors = db.session.query(Author).all()
    return render_template('authors.html', authors=authors, msg=f'The Author deleted successfully.')
  except Exception:
    db.session.rollback()
    authors = db.session.query(Author).all()

    return render_template('authors.html', authors=authors, msg='Database error. Please try again.')



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)









# with app.app_context():
#   db.create_all()
