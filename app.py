from flask import Flask, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"

db.init_app(app)


@app.route('/')
def home():
  books = db.session.query(Book) \
    .all()
  authors = db.session.query(Author)\
    .all()
  return render_template('home.html', books=books, authors=authors)




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



if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)









#with app.app_context():
  #db.create_all()
