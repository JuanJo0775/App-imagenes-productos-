from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario
from app.auth.forms import RegistroForm, LoginForm
import logging

auth = Blueprint('auth', __name__)

# Configurar logging para mejor seguimiento de errores
logger = logging.getLogger(__name__)


@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistroForm()
    if form.validate_on_submit():
        try:
            # Generar hash de la contraseña
            hashed_password = bcrypt.generate_password_hash(form.contrasena.data).decode('utf-8')

            # Crear nuevo usuario
            usuario = Usuario(
                nombre_usuario=form.nombre_usuario.data,
                email=form.email.data,
                contrasena=hashed_password,
                es_admin=False  # Por defecto, los usuarios nuevos no son administradores
            )

            # Guardar en la base de datos
            db.session.add(usuario)
            db.session.commit()

            flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            # Registrar el error y hacer rollback de la transacción
            logger.error(f"Error en registro: {str(e)}")
            db.session.rollback()
            flash('Ocurrió un error al crear tu cuenta. Por favor, intenta nuevamente.', 'danger')

    return render_template('auth/registro.html', title='Registro', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            usuario = Usuario.query.filter_by(email=form.email.data).first()

            # Verificar si el usuario existe
            if usuario is None:
                flash('Email no registrado. Por favor, verifica tus datos.', 'danger')
                return render_template('auth/login.html', title='Iniciar Sesión', form=form)

            # Verificar contraseña con manejo de excepciones
            try:
                password_correct = bcrypt.check_password_hash(usuario.contrasena, form.contrasena.data)
            except ValueError as e:
                # Error específico para "Invalid salt"
                logger.error(f"Error al verificar contraseña: {str(e)}")
                flash(
                    'Problema con la verificación de contraseña. Por favor, restablece tu contraseña o contacta a soporte.',
                    'danger')
                return render_template('auth/login.html', title='Iniciar Sesión', form=form)

            if password_correct:
                login_user(usuario, remember=form.recordar.data)

                # Redirigir a la página que el usuario intentaba acceder
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash('Contraseña incorrecta. Por favor, intenta nuevamente.', 'danger')

        except Exception as e:
            # Manejo general de excepciones
            logger.error(f"Error inesperado en login: {str(e)}")
            flash('Ocurrió un error al iniciar sesión. Por favor, intenta más tarde.', 'danger')

    return render_template('auth/login.html', title='Iniciar Sesión', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('main.index'))


# Ruta adicional para crear un usuario administrador (solo para desarrollo)
@auth.route('/crear-admin', methods=['GET'])
def crear_admin():
    # Solo permitir esto en ambiente de desarrollo
    if not app.config.get('DEBUG', False):
        abort(404)

    # Verificar si ya existe un admin
    if Usuario.query.filter_by(es_admin=True).first():
        flash('Ya existe un usuario administrador', 'info')
        return redirect(url_for('main.index'))

    try:
        # Crear usuario admin
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = Usuario(
            nombre_usuario='admin',
            email='admin@example.com',
            contrasena=hashed_password,
            es_admin=True
        )
        db.session.add(admin)
        db.session.commit()

        flash('Usuario administrador creado. Email: admin@example.com, Contraseña: admin123', 'success')
    except Exception as e:
        logger.error(f"Error al crear admin: {str(e)}")
        db.session.rollback()
        flash('Error al crear el usuario administrador', 'danger')

    return redirect(url_for('main.index'))