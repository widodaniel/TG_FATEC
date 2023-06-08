from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()], render_kw={"placeholder": "Digite seu e-mail"})
    senha = PasswordField("Senha", validators=[DataRequired()], render_kw={"placeholder": "Digite sua senha"})

class EditarPerfil(FlaskForm):
    email = StringField("Email", render_kw={"placeholder": "Digite seu e-mail"})
    senha = PasswordField("Senha", render_kw={"placeholder": "Digite sua senha"})