from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from app.config import Config

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Configurar login_manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página'
    login_manager.login_message_category = 'info'

    # Registrar blueprints
    from app.auth.routes import auth
    from app.admin.routes import admin
    from app.productos.routes import productos
    from app.usuarios.routes import usuarios
    from app.main.routes import main

    app.register_blueprint(auth)
    app.register_blueprint(admin)
    app.register_blueprint(productos)
    app.register_blueprint(usuarios)
    app.register_blueprint(main)

    # Crear tablas en la base de datos si no existen
    with app.app_context():
        db.create_all()

    return app