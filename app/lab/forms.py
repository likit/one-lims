from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField
from wtforms.validators import InputRequired


class ChoiceItemForm(FlaskForm):
    result = StringField('Result', validators=[
        InputRequired()
    ])
    interpretation = StringField('Interpretation', validators=[
        InputRequired()
    ])
    ref = BooleanField('Is this a reference value?')