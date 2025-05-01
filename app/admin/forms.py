from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from app import db
from app.models import Categoria

class ProductoForm(FlaskForm):
    nombre = StringField('Nombre del Producto',
                       validators=[DataRequired(), Length(min=2, max=100)])
    descripcion = TextAreaField('Descripción',
                              validators=[Optional()])
    ficha_tecnica = TextAreaField('Ficha Técnica',
                                validators=[Optional()])
    id_categoria = SelectField('Categoría',
                             coerce=int,
                             validators=[DataRequired()])
    submit = SubmitField('Guardar')

class CategoriaForm(FlaskForm):
    nombre_categoria = StringField('Nombre de la Categoría',
                              validators=[DataRequired(), Length(min=2, max=100)])
    submit = SubmitField('Guardar')

class ImagenProductoForm(FlaskForm):
    nombre = StringField('Nombre de la Imagen (opcional)',
                       validators=[Optional(), Length(max=255)])
    imagen = FileField('Imagen',
                     validators=[
                         FileRequired(),
                         FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo se permiten imágenes')
                     ])
    submit = SubmitField('Subir Imagen')

class VideoProductoForm(FlaskForm):
    nombre = StringField('Nombre del Video (opcional)',
                       validators=[Optional(), Length(max=255)])
    video = FileField('Video',
                    validators=[
                        FileRequired(),
                        FileAllowed(['mp4', 'webm', 'ogg'], 'Solo se permiten videos MP4, WebM y OGG')
                    ])
    submit = SubmitField('Subir Video')

class ImagenCategoriaForm(FlaskForm):
    nombre = StringField('Nombre de la Imagen (opcional)',
                       validators=[Optional(), Length(max=255)])
    imagen = FileField('Imagen',
                     validators=[
                         FileRequired(),
                         FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo se permiten imágenes')
                     ])
    submit = SubmitField('Subir Imagen')