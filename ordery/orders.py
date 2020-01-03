from flask import (Blueprint, flash, g, redirect,
                    render_template, request, url_for, session)
from werkzeug.exceptions import abort
from . forms import AddOrdersForm, LoginForm,CSVForm,SearchForm
from ordery.db import get_db
from flask_login import login_required, login_user, logout_user, current_user
from . auth import login_required
from werkzeug.utils import secure_filename
import os
from flask import current_app
from . product_csv import product_csv
from . order_csv import order_csv
from . date import create_date_table, create_view, get_weekly_data, convert_row_list, convert_row_list_key
from flask import g
bp = Blueprint('orders', __name__)

@bp.route('/', methods=['GET', 'POST'])
# @login_required
def index():
    db = get_db()
    form = AddOrdersForm()
    if request.method == 'GET':
        orders = db.execute(
        'SELECT id, ord_nbr, ord_date, ord_qty, prod_id FROM orders ORDER BY ord_date DESC'
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
# @login_required
def delete(id):
    order = get_order(id)
    db = get_db()
    db.execute('DELETE FROM orders WHERE id = ?', (id,))
    db.commit()
    flash('You have delete an order')
    return redirect(url_for('orders.index'))

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
# @login_required
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
# @login_required
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

    return render_template('csv.html', form=form)


@bp.route('/dashboard', methods=('GET', 'POST'))
# @login_required
def dashboard():
    create_date_table()
    db = get_db()
    best_sellers = db.execute(''' SELECT P.prod_nbr,
        price * ord_qty AS Total_Sales
      FROM products P
         INNER JOIN orders O ON P.id = O.prod_id
      GROUP BY P.id
      ORDER BY Total_Sales DESC
      Limit 1
    ;''').fetchone()
    total_amount = db.execute('''SELECT SUM (Total_Sales) AS total
        FROM (
        SELECT price * ord_qty AS Total_Sales
          FROM products P
             INNER JOIN orders O ON P.id = O.prod_id
         );''').fetchone()
    total_orders = db.execute('''  SELECT
            count(ord_nbr) AS Order_Count,
            sum(ord_qty)   AS Order_Quauntity
          FROM products P
            INNER JOIN orders O ON P.id = O.prod_id;
        ''').fetchone()
    sales_record = db.execute('''SELECT date, sum(ord_qty) AS sum_ord_qty
            FROM products P
              INNER JOIN orders O ON P.id       = O.prod_id
              INNER JOIN dates  D ON O.ord_date = D.date
           GROUP BY date
order by sum_ord_qty desc
limit 1;
    ''').fetchone()
    return render_template('dashboard.html', sales_record = sales_record,best_sellers = best_sellers, total_orders = total_orders,total_amount = total_amount)


@bp.route('/report', methods=('GET', 'POST'))
# @login_required
def report():
    db = get_db()
    create_view()
    #labels = ["SUNDAY", "MONDAY", "TUESDAY","WEDNESDAY", "THURSDAY","FRIDAY","SATURDAY"]
    #labels1 = ['JUL', 'AUG', 'SEP']
    ord_qty_rows = db.execute('SELECT sum(ord_qty) as total, day_name FROM v_ord group by day_name order by total desc;').fetchall()
    values = convert_row_list(ord_qty_rows)
    labels =convert_row_list_key(ord_qty_rows)
    ord_amt_rows =db.execute('SELECT sum(ord_amt), month FROM v_ord group by month order by month asc;').fetchall()
    values1 = convert_row_list(ord_amt_rows)
    labels1 = convert_row_list_key(ord_amt_rows)
    ord_amt_pro_nbr_rows = db.execute('SELECT sum(ord_amt), prod_nbr FROM v_ord group by prod_nbr order by sum(ord_amt) desc;').fetchall()
    values2 = convert_row_list(ord_amt_pro_nbr_rows)
    labels2 = convert_row_list_key(ord_amt_pro_nbr_rows)
    ord_qty_color_rows = db.execute('SELECT sum(ord_qty),  color FROM v_ord group by color;').fetchall()
    values3 = convert_row_list(ord_qty_color_rows)
    labels3 = convert_row_list_key(ord_qty_color_rows)
    ord_qty_size_rows = db.execute('SELECT sum(ord_qty), size FROM v_ord group by size').fetchall()
    values4 = convert_row_list(ord_qty_size_rows)
    labels4  = convert_row_list_key(ord_qty_size_rows)
    return render_template('report.html', values=values, labels=labels,
        labels1=labels1,labels2=labels2, values1 = values1, values2 = values2,
        labels3 = labels3, values3 = values3, labels4 = labels4, values4 = values4)

@bp.before_app_request
def before_request():
    g.search_form = SearchForm()
