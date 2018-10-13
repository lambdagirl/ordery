from flask import (Blueprint, flash, g, redirect,
                    render_template, request, url_for, session)
from werkzeug.exceptions import abort
from . forms import AddOrdersForm, LoginForm, AddProductsForm,CSVForm,SearchForm
from ordery.db import get_db
from flask_login import login_required, login_user, logout_user, current_user
from . auth import login_required

bp = Blueprint('products', __name__, url_prefix='/products')

@bp.route('/', methods=['GET', 'POST'])
@login_required
def pd_index():
    db = get_db()
    form = AddProductsForm()
    if request.method == 'GET':
        products = db.execute(
        'SELECT id, prod_nbr,  prod_line,  size, color, price FROM products'
        ).fetchall()
        return render_template('products.html', products = products, form = form)
    else:
        if form.validate_on_submit():
            db = get_db()
            prod_nbr = form.prod_nbr.data
            prod_line = form.prod_line.data
            size = form.size.data
            color = form.color.data
            price = form.price.data
            db.execute(
                'INSERT INTO products (prod_nbr, prod_line, size, color, price)'
                ' VALUES (?, ?, ?, ?, ?)',
                (prod_nbr, prod_line,  size, color, price)
            )
            db.commit()
            flash('You have add a new product!')
        else:
            flash(form.errors)
    return redirect(url_for('products.pd_index'))


def get_product(id):
    product = get_db().execute(
        'SELECT id, prod_nbr,  prod_line,  size, color, price FROM products'
        ' WHERE id = ?',
        (id,)
    ).fetchone()
    if product is None:
        abort(404, "Product id {0} doesn't exist.".format(id))
    return product

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_product(id):
        product = get_product(id)
        form = AddProductsForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                prod_nbr = form.prod_nbr.data
                prod_line = form.prod_line.data
                size = form.size.data
                color = form.color.data
                price = form.price.data
                db = get_db()
                db.execute(
                'UPDATE products SET prod_nbr = ?, prod_line = ?, size = ?, color =?, price =? WHERE id = ?',
                (prod_nbr, prod_line, size, color, price, id)
                )
                db.commit()
                flash('You have modify a product')
                return redirect(url_for('products.pd_index'))
        elif request.method == 'GET':
            form.prod_nbr.data = product['prod_nbr']
            form.prod_line.data = product['prod_line']
            form.size.data = product['size']
            form.color.data = product['color']
            form.price.data = product['price']
        return render_template('update.html', form=form)


@bp.route('/search')
@login_required
def search():
        if not g.search_form.validate():
            return redirect(url_for('orders.index'))
        db = get_db()
        word = g.search_form.q.data
        products = db.execute('''SELECT rowid, prod_nbr, prod_line, size, color, price
                    FROM products_index
                    WHERE Products_index
                    MATCH ?''', (word,)
                    ).fetchall()
        return render_template('search.html', products = products)
