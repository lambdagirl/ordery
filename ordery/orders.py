from flask import (Blueprint, flash, g, redirect,
                    render_template, request, url_for, session)
from werkzeug.exceptions import abort
from . forms import AddOrdersForm, LoginForm,CSVForm
from ordery.db import get_db
from flask_login import login_required, login_user, logout_user, current_user
from . auth import login_required
from werkzeug.utils import secure_filename
import os
from flask import current_app
from . product_csv import product_csv
from . order_csv import order_csv
from . date import create_date_table, create_view, get_weekly_data

bp = Blueprint('orders', __name__)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    db = get_db()
    form = AddOrdersForm()
    if request.method == 'GET':
        orders = db.execute(
        'SELECT id, ord_nbr, ord_date, ord_qty, prod_id FROM orders'
        ).fetchall()
        return render_template('orders.html', orders = orders, form = form)
    else:
        if form.validate_on_submit():
            db = get_db()
            ord_nbr = form.ord_nbr.data
            ord_date = form.ord_date.data
            ord_qty = form.ord_qty.data
            prod_id = form.prod_id.data
            db.execute(
                'INSERT INTO orders (ord_nbr, ord_date, ord_qty, prod_id)'
                ' VALUES (?, ?, ?, ?)',
                (ord_nbr, ord_date, ord_qty, prod_id)
            )
            db.commit()
            flash('You have add a new order!')
        else:
            flash(form.errors)
    return redirect(url_for('orders.index'))


def get_order(id):
    order = get_db().execute(
        'SELECT id, ord_nbr, ord_date, ord_qty, prod_id FROM orders'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if order is None:
        abort(404, "Order id {0} doesn't exist.".format(id))

    return order


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    order = get_order(id)
    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (id,))
    db.commit()
    flash('You have delete an order')
    return redirect(url_for('orders.index'))

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
        order = get_order(id)
        form = AddOrdersForm()
        #form.prod_id.choices = v_prod_id()
        if request.method == 'POST':
            if form.validate_on_submit():
                ord_nbr = form.ord_nbr.data
                ord_date = form.ord_date.data
                ord_qty = form.ord_qty.data
                prod_id = form.prod_id.data
                db = get_db()
                db.execute(
                'UPDATE orders SET ord_nbr = ?, ord_date = ?, ord_qty = ?, prod_id =? WHERE id = ?',
                (ord_nbr, ord_date, ord_qty, prod_id, id)
                )
                db.commit()
                flash('You have modify an order')
                return redirect(url_for('orders.index'))
        elif request.method == 'GET':
            form.ord_nbr.data = order['ord_nbr']
            form.ord_date.data = order['ord_date']
            form.ord_qty.data = order['ord_qty']
            form.prod_id.data = order['prod_id']
        return render_template('update.html', form=form)




@bp.route('/csv', methods=('GET', 'POST'))
@login_required
def upload_csv():
    form = CSVForm()
    if form.validate_on_submit():
        f = form.csv.data
        filename = secure_filename(f.filename)
    #    f.save(current_app.config['UPLOAD_FOLDER'], 'csv', filename)
        f.save(secure_filename(f.filename))
        if form.description.data == "Product":
            product_csv(filename)
            flash("Products has been loaded!")
            return redirect(url_for('products.pd_index'))
        if form.description.data == "Order":
            order_csv(filename)
            flash("orders has been loaded!")

            return redirect(url_for('orders.index'))
        else:
            flash("Please enter valid type!")
        create_date_table()
        create_view()
    return render_template('csv.html', form=form)


@bp.route('/report', methods=('GET', 'POST'))
@login_required
def report():
    db = get_db()
    labels = ["SUNDAY", "MONDAY", "TUESDAY","WEDNESDAY", "THURSDAY","FRIDAY","SATURDAY"]
    rows = db.execute('SELECT ord_amt, day_name FROM v_ord;').fetchall()
    values = get_weekly_data(rows)
    print(values)

    return render_template('report.html', values=values, labels=labels)
