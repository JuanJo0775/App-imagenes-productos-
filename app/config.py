import os
from datetime import timedelta


class Config:
    # Configuración básica
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_super_secreta_para_desarrollo'

    # Configuración de la base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL') or 'mysql+pymysql://root:@localhost/parcial_db_24_04_2025'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de archivos subidos
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')
    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'ogg'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # Configuración de la sesión
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Configuración de paginación
    PRODUCTOS_PER_PAGE = 12  # 3 filas de 4 productos en la vista de cuadrícula