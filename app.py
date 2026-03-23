from flask import Flask, request, render_template, session, redirect, url_for
import os
from data_models import db, Author, Book


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)

def fetch_books_and_authors():
  books = db.session.query(Book, Author) \
    .join(Author, Book.author_id == Author.id) \
    .all()
  return books

@app.route('/')
def home():
  books = fetch_books_and_authors()
  return render_template('home.html', books=books)


@app.route('/sort_by_title', methods=['post'])
def sort_title():
  books = db.session.query(Book, Author) \
    .join(Author, Book.author_id == Author.id) \
    .order_by(Book.title) \
    .all()
  return render_template('home.html', books=books)



@app.route('/sort_by_author', methods=['post'])
def sort_author():
  books = db.session.query(Book, Author) \
    .join(Author, Book.author_id == Author.id) \
    .order_by(Author.name) \
    .all()
  return render_template('home.html', books=books)


@app.route('/search', methods=['POST'])
def search():
  to_find = request.form.get('search')
  books = db.session.query(Book, Author) \
    .join(Author, Book.author_id == Author.id) \
    .filter(Book.title.contains(to_find)) \
    .all()
  if not books:
    return render_template("search.html", msg="no books found")
  return render_template('search.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
  if request.method == 'GET':
    return render_template('add_author.html')
  add_name = request.form.get('name', '')
  add_birth_date = request.form.get('birthdate', '')
  add_date_of_death = request.form.get('date_of_death', '')

  author = Author(
    name = add_name,
    birth_date = add_birth_date,
    date_of_death = add_date_of_death
  )
  db.session.add(author)
  db.session.commit()
  msg = f'The author {add_name} has been added successfully!'
  return render_template('add_author.html', msg=msg)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
  authors = db.session.query(Author) \
    .all()
  if request.method == 'GET':
    return render_template('add_book.html', authors=authors)
  add_isbn = request.form.get('isbn')
  add_title = request.form.get('title')
  add_publication_year = request.form.get('publication_year')
  add_author_id = request.form.get('authors')

  book = Book(
    isbn = add_isbn,
    title = add_title,
    publication_year = add_publication_year,
    author_id = add_author_id
  )
  db.session.add(book)
  db.session.commit()
  msg = f"The book {add_title} has been added successfully"
  return render_template('add_book.html', authors=authors, msg=msg)



@app.route('/book/<int:book_id>/delete', methods=['post'])
def delete_book(book_id):
  db.session.query(Book) \
    .filter(Book.id==book_id) \
    .delete()
  db.session.commit()
  return redirect(url_for('home'))



@app.route('/authors')
def view_authors():
  authors = db.session.query(Author) \
    .all()
  return render_template('authors.html', authors=authors)



@app.route('/authors/<int:author_id>/delete', methods=['post'])
def delete_author(author_id):
  db.session.query(Author) \
    .filter(Author.id == author_id) \
    .delete()
  db.session.commit()
  return redirect(url_for('view_authors'))



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)









#with app.app_context():
  #db.create_all()
