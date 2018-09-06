from flask import render_template, flash, redirect, session, url_for, request, g
from bookstore import app, db, bootstrap, login_manager
from wtforms import ValidationError
from .models import Book, Author, User, Role, Association, Order, admin_permission
from .forms import LoginForm, RegistrationForm, CreateBookForm, CreateAuthorForm, DeleteBookForm, DeleteAuthorForm, UpdateBookForm, UpdateAuthorForm, AddAuthorForm, UploadUpdate
from flask_login import login_required, login_user, logout_user, current_user
from .decorators import admin_required


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/books')
def books():
    items = Book.query.all()
    return render_template("books.html", items = items)


@app.route('/authors')
def authors():
    items = Author.query.all()
    return render_template("authors.html", items = items)


@app.route('/books/<book>')
def detail_book(book):
    book = Book.query.get_or_404(book)
    return render_template("detail_book.html", item = book)


@app.route('/authors/<name>')
def detail_author(name):
    name = Author.query.get_or_404(name)
    return render_template("detail_author.html", item = name)


@app.route('/store/<int:id>/image')
def book_image(id):
    book = Book.query.get_or_404(id)
    return app.response_class(book.image, mimetype='application/octet-stream')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('index'))
        flash('Неверное имя или пароль')
    return render_template("login.html", form = form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.create(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    number=form.number.data)
        flash('Теперь вы можете войти в систему')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/lk')
@login_required
@admin_required
def lk():
    return render_template('lk.html')


@app.route('/lk/create', methods=['GET', 'POST'])
@login_required
@admin_required
def lk_create():
    authorform = CreateAuthorForm()
    if authorform.submit_author.data and authorform.validate():
        author = Author.create(name=authorform.author.data)
        flash('Вы создали автора')
        return redirect(url_for('lk'))

    bookform = CreateBookForm()
    if bookform.submit_book.data and bookform.validate():
        file = request.files['image']
        new_file = file.read()
        book = Book.create(book=bookform.name.data,
                    type=bookform.type.data,
                    description=bookform.description.data,
                    price=bookform.price.data,
                    authors=[bookform.authors.data],
                    image=new_file)
        flash('Вы создали книгу')
        return redirect(url_for('lk'))
    return render_template('lk_create.html', bookform=bookform, authorform=authorform)


@app.route('/lk/update', methods=['GET', 'POST'])
@login_required
@admin_required
def lk_update():
    authorform = UpdateAuthorForm()
    if authorform.submit_author.data and authorform.validate():
        author = Author.query.get_or_404(request.form['name'])
        author.update(name=authorform.author.data)
        flash('Вы изменили имя автора')
        return redirect(url_for('lk'))

    bookform = UpdateBookForm()
    if bookform.submit_book.data and bookform.validate():
        book = Book.query.get_or_404(request.form['choose_book'])
        book.update(book=bookform.name.data,
                    type=bookform.type.data,
                    description=bookform.description.data,
                    price=bookform.price.data)
        flash('Вы изменили данные в книге')
        return redirect(url_for('lk'))

    addform = AddAuthorForm(request.form)
    if addform.submit_add.data and addform.validate():
        add = Association.create(
                            books=request.form['book'],
                            authors=request.form['author']
                            )
        flash('Вы добавили автора')
        return redirect(url_for('lk'))

    imageform = UploadUpdate()
    if imageform.submit_image.data and imageform.validate():
        get_file = request.files['new_image']
        file = get_file.read()
        book = Book.query.get_or_404(request.form['book_name'])
        book.update(image=file)
        flash('Вы обновили обложку')
        return redirect(url_for('lk'))
    return render_template('lk_update.html', authorform=authorform, bookform=bookform, addform=addform, imageform=imageform)


@app.route('/lk/delete', methods=['GET', 'POST'])
@login_required
@admin_required
def lk_delete():
    authorform = DeleteAuthorForm(request.form)
    bookform = DeleteBookForm(request.form)

    if authorform.submit_author.data and authorform.validate():
        author = Author.query.get_or_404(request.form['name'])
        author.delete()
        flash('Вы удалили автора')
        return redirect(url_for('lk'))

    if bookform.submit_book.data and bookform.validate():
        book = Book.query.get_or_404(request.form['name'])
        book.delete()
        flash('Вы удалили книгу')
        return redirect(url_for('lk'))
    return render_template('lk_delete.html', authorform=authorform, bookform=bookform)


@app.route('/search')
def search():
    query = request.args.get('q')
    authors = Author.query.whoosh_search(query).all()
    books = Book.query.whoosh_search(query).all()
    return render_template('search.html', authors=authors, books=books, query=query)


@app.route('/cart')
@login_required
def cart():
    orders = Order.query.filter_by(user=current_user.username, status='создан').all()
    return render_template('cart.html', orders=orders)


@app.route('/cart/in_work')
@login_required
def orders_in_work():
    orders = Order.query.filter(Order.user==current_user.username, Order.status!='создан').all()
    return render_template('orders_in_work.html', orders=orders)


@app.route('/books/buy/<id>', methods=['POST', 'GET'])
@login_required
def buy_book(id):
    book = Book.query.get_or_404(id)
    order = Order.create(
                user = current_user.username,
                book = book.book,
                email = current_user.email,
                price = book.price,
                number = current_user.number,
                status = 'создан')
    return redirect(url_for('cart'))


@app.route('/delete/<id>', methods=['POST', 'GET'])
@login_required
def delete_order(id):
    order = Order.query.get_or_404(id)
    order.delete()
    if current_user.role_id == admin_permission:
        return redirect(url_for('lk_orders'))
    else:
        return redirect(url_for('cart'))


@app.route('/work', methods=['POST', 'GET'])
@login_required
def work():
    orders = Order.query.filter_by(user=current_user.username).all()
    for order in orders:
        order.update(status='заказ в обработке')
    return redirect(url_for('cart'))


@app.route('/lk/orders', methods=['GET', 'POST'])
@login_required
@admin_required
def lk_orders():
    orders = Order.query.filter(Order.status!='создан').all()
    return render_template('lk_orders.html', orders=orders)


@app.route('/lk/work/<id>', methods=['GET', 'POST'])
@login_required
@admin_required
def lk_work(id):
    order = Order.query.get(id)
    order.update(status='В работе')
    return redirect(url_for('lk_orders'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500
