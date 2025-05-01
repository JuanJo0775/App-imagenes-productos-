from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from app.models import Usuario


class UpdatePerfilForm(FlaskForm):
    nombre_usuario = StringField('Nombre de Usuario',
                                 validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Actualizar')

    def validate_email(self, email):
        if email.data != current_user.email:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Este email ya está registrado. Por favor, elige otro.')

    def validate_nombre_usuario(self, nombre_usuario):
        if nombre_usuario.data != current_user.nombre_usuario:
            usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario.data).first()
            if usuario:
                raise ValidationError('Este nombre de usuario ya está en uso. Por favor, elige otro.')


class CambiarContrasenaForm(FlaskForm):
    contrasena_actual = PasswordField('Contraseña Actual',
                                      validators=[DataRequired()])
    nueva_contrasena = PasswordField('Nueva Contraseña',
                                     validators=[DataRequired(), Length(min=6)])
    confirmar_contrasena = PasswordField('Confirmar Nueva Contraseña',
                                         validators=[DataRequired(), EqualTo('nueva_contrasena')])
    submit = SubmitField('Cambiar Contraseña')