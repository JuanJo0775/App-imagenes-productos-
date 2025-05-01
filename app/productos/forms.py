from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

class ResenaForm(FlaskForm):
    comentario = TextAreaField('Comentario',
                             validators=[Optional(), Length(max=1000)])
    puntuacion = IntegerField('Puntuación (1-5 estrellas)',
                           validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Enviar Reseña')

class FiltroProductosForm(FlaskForm):
    categoria = SelectField('Categoría', coerce=int, validators=[Optional()])
    ordenar_por = SelectField('Ordenar por', choices=[
        ('fecha_desc', 'Más recientes'),
        ('fecha_asc', 'Más antiguos'),
        ('likes_desc', 'Más likes'),
        ('likes_asc', 'Menos likes'),
        ('nombre_asc', 'Nombre (A-Z)'),
        ('nombre_desc', 'Nombre (Z-A)')
    ])
    submit = SubmitField('Filtrar')

class BusquedaForm(FlaskForm):
    q = StringField('Buscar', validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Buscar')