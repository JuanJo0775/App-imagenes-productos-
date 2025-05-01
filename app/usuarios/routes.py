from flask import Blueprint, render_template, url_for, flash, redirect, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Usuario, Favorito, Producto, Resena
from app.usuarios.forms import UpdatePerfilForm, CambiarContrasenaForm
from sqlalchemy import desc

usuarios = Blueprint('usuarios', __name__)


@usuarios.route('/perfil')
@login_required
def perfil():
    return render_template('usuarios/perfil.html', title='Mi Perfil')


@usuarios.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = UpdatePerfilForm()

    if form.validate_on_submit():
        current_user.nombre_usuario = form.nombre_usuario.data
        current_user.email = form.email.data
        db.session.commit()
        flash('¡Tu perfil ha sido actualizado!', 'success')
        return redirect(url_for('usuarios.perfil'))
    elif request.method == 'GET':
        form.nombre_usuario.data = current_user.nombre_usuario
        form.email.data = current_user.email

    return render_template('usuarios/editar_perfil.html', title='Editar Perfil', form=form)


@usuarios.route('/perfil/cambiar_contrasena', methods=['GET', 'POST'])
@login_required
def cambiar_contrasena():
    form = CambiarContrasenaForm()

    if form.validate_on_submit():
        # Verificar que la contraseña actual sea correcta
        if bcrypt.check_password_hash(current_user.contrasena, form.contrasena_actual.data):
            hashed_password = bcrypt.generate_password_hash(form.nueva_contrasena.data).decode('utf-8')
            current_user.contrasena = hashed_password
            db.session.commit()
            flash('¡Tu contraseña ha sido actualizada!', 'success')
            return redirect(url_for('usuarios.perfil'))
        else:
            flash('Contraseña incorrecta. Por favor, intenta nuevamente.', 'danger')

    return render_template('usuarios/cambiar_contrasena.html', title='Cambiar Contraseña', form=form)


@usuarios.route('/favoritos')
@login_required
def favoritos():
    page = request.args.get('page', 1, type=int)

    # Obtener productos favoritos del usuario actual
    favoritos_paginados = db.session.query(Producto). \
        join(Favorito, Favorito.id_producto == Producto.id_producto). \
        filter(Favorito.id_usuario == current_user.id_usuario). \
        order_by(desc(Favorito.fecha_agregado)). \
        paginate(page=page, per_page=12, error_out=False)

    return render_template(
        'usuarios/favoritos.html',
        title='Mis Favoritos',
        productos=favoritos_paginados
    )


@usuarios.route('/mis_resenas')
@login_required
def mis_resenas():
    page = request.args.get('page', 1, type=int)
    puntaje = request.args.get('puntaje', type=int)
    tipo = request.args.get('tipo')

    # Construir consulta base
    query = Resena.query.filter_by(id_usuario=current_user.id_usuario)

    # Aplicar filtros si se proporcionan
    if puntaje:
        query = query.filter_by(puntuacion=puntaje)

    if tipo:
        query = query.filter_by(tipo_comentario=tipo)

    # Obtener las reseñas paginadas
    resenas_paginadas = query.order_by(desc(Resena.fecha_hora)).paginate(
        page=page, per_page=10, error_out=False
    )

    return render_template(
        'usuarios/mis_resenas.html',
        title='Mis Reseñas',
        resenas=resenas_paginadas
    )


@usuarios.route('/resenas/<int:resena_id>/eliminar', methods=['POST'])
@login_required
def eliminar_resena(resena_id):
    resena = Resena.query.get_or_404(resena_id)

    # Verificar que la reseña pertenece al usuario actual
    if resena.id_usuario != current_user.id_usuario:
        abort(403)  # Forbidden

    producto = Producto.query.get(resena.id_producto)

    # Actualizar contadores en el producto
    if resena.tipo_comentario == 'positivo':
        producto.comentarios_positivos = max(0, producto.comentarios_positivos - 1)
    else:
        producto.comentarios_negativos = max(0, producto.comentarios_negativos - 1)

    # Eliminar la reseña
    db.session.delete(resena)
    db.session.commit()

    flash('Reseña eliminada con éxito', 'success')
    return redirect(url_for('usuarios.mis_resenas'))