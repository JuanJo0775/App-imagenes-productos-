from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_user, current_user, logout_user, login_required
from app import db, bcrypt
from app.models import Usuario
from app.auth.forms import RegistroForm, LoginForm

auth = Blueprint('auth', __name__)


@auth.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistroForm()
    if form.validate_on_submit():
        # Generar hash de la contraseña
        hashed_password = bcrypt.generate_password_hash(form.contrasena.data).decode('utf-8')

        # Crear nuevo usuario
        usuario = Usuario(
            nombre_usuario=form.nombre_usuario.data,
            email=form.email.data,
            contrasena=hashed_password
        )

        # Guardar en la base de datos
        db.session.add(usuario)
        db.session.commit()

        flash('¡Tu cuenta ha sido creada! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/registro.html', title='Registro', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()

        # Verificar si el usuario existe y la contraseña es correcta
        if usuario and bcrypt.check_password_hash(usuario.contrasena, form.contrasena.data):
            login_user(usuario, remember=form.recordar.data)

            # Redirigir a la página que el usuario intentaba acceder
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Error al iniciar sesión. Verifica tu email y contraseña', 'danger')

    return render_template('auth/login.html', title='Iniciar Sesión', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))