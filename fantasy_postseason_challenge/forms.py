from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm', message='Passwords must match.')
    ])
    confirm = PasswordField('Repeat Password')
    display_name = StringField('Display Name', validators=[DataRequired(), Length(min=2, max=50)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SelectTeamForm(FlaskForm):
    QB = SelectField("QB")
    RB1 = SelectField("RB1")
    RB2 = SelectField("RB2")
    WR1 = SelectField("WR1")
    WR2 = SelectField("WR2")
    TE = SelectField("TE")
    FLEX = SelectField("FLEX")
    K = SelectField("K")
    D_ST = SelectField("D/ST")

    