from flask_wtf import FlaskForm
from wtforms import Form,StringField,SubmitField, TextAreaField, DateTimeField, IntegerField, PasswordField, SelectField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask import request


class CSVForm(FlaskForm):
    csv = FileField(validators=[FileRequired()])
    description  = StringField(u'Data Type("Product"/"Order")')
    submit = SubmitField('Submit')


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('Submit')


class AddOrdersForm(FlaskForm):
    ord_nbr = IntegerField('order number', validators = [DataRequired()])
    ord_date = StringField('order date', validators = [DataRequired()])
    ord_qty = IntegerField('order quantity', validators = [DataRequired()])
    prod_id = IntegerField('product_id', validators = [DataRequired()])
    #prod_id = SelectField('product_id', choices=[],coerce=int)

    submit = SubmitField('Submit')

class AddProductsForm(FlaskForm):
    prod_nbr = StringField('product number', validators = [DataRequired()])
    prod_line = StringField('line', validators = [DataRequired()])
    size = StringField('size', validators = [DataRequired()])
    color = StringField('color', validators = [DataRequired()])
    price = IntegerField('price', validators = [DataRequired()])
    submit = SubmitField('Submit')



class SearchForm(FlaskForm):
    q = StringField('Search', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
