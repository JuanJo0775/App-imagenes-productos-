from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario


class RegistroForm(FlaskForm):
    nombre_usuario = StringField('Nombre de Usuario',
                                 validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    contrasena = PasswordField('Contraseña',
                               validators=[DataRequired(), Length(min=6)])
    confirmar_contrasena = PasswordField('Confirmar Contraseña',
                                         validators=[DataRequired(), EqualTo('contrasena')])
    submit = SubmitField('Registrarse')

    # Custom validator for email
    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email ya está registrado. Por favor, elige otro.')

    # Custom validator for username
    def validate_nombre_usuario(self, nombre_usuario):
        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario.data).first()
        if usuario:
            raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    contrasena = PasswordField('Contraseña',
                               validators=[DataRequired()])
    recordar = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')