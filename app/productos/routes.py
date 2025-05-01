from flask import Blueprint, render_template, url_for, flash, redirect, request, jsonify, current_app, abort
from flask_login import current_user, login_required
from app import db
from app.models import Producto, Categoria, Resena, InteraccionProducto, Favorito, ImagenProducto, VideoProducto
from app.productos.forms import ResenaForm
import os
from datetime import datetime
from sqlalchemy import desc

productos = Blueprint('productos', __name__)


@productos.route('/producto/<int:producto_id>')
def ver_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ResenaForm()

    # Obtener todas las reseñas del producto
    resenas = Resena.query.filter_by(id_producto=producto_id).order_by(desc(Resena.fecha_hora)).all()

    # Verificar si el usuario ha dado like/dislike o marcado como favorito
    user_interaction = None
    is_favorite = False

    if current_user.is_authenticated:
        user_interaction = InteraccionProducto.query.filter_by(
            id_usuario=current_user.id_usuario,
            id_producto=producto_id
        ).first()

        favorite = Favorito.query.filter_by(
            id_usuario=current_user.id_usuario,
            id_producto=producto_id
        ).first()

        is_favorite = favorite is not None

    # Obtener productos relacionados (misma categoría)
    relacionados = []
    if producto.id_categoria:
        relacionados = Producto.query.filter(
            Producto.id_categoria == producto.id_categoria,
            Producto.id_producto != producto.id_producto
        ).limit(4).all()

    return render_template(
        'productos/detalle.html',
        title=producto.nombre,
        producto=producto,
        resenas=resenas,
        form=form,
        user_interaction=user_interaction,
        is_favorite=is_favorite,
        relacionados=relacionados
    )


@productos.route('/categoria/<int:categoria_id>')
def por_categoria(categoria_id):
    page = request.args.get('page', 1, type=int)
    categoria = Categoria.query.get_or_404(categoria_id)

    productos_list = Producto.query.filter_by(
        id_categoria=categoria_id
    ).order_by(
        desc(Producto.fecha_ingreso)
    ).paginate(
        page=page,
        per_page=12,
        error_out=False
    )

    return render_template(
        'productos/por_categoria.html',
        title=f'Categoría: {categoria.nombre_categoria}',
        categoria=categoria,
        productos=productos_list
    )


@productos.route('/producto/<int:producto_id>/resena', methods=['POST'])
@login_required
def agregar_resena(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ResenaForm()

    if form.validate_on_submit():
        # Determinar si es un comentario positivo o negativo basado en la puntuación
        tipo_comentario = 'positivo' if form.puntuacion.data >= 3 else 'negativo'

        # Crear la reseña
        resena = Resena(
            id_producto=producto.id_producto,
            id_usuario=current_user.id_usuario,
            comentario=form.comentario.data,
            puntuacion=form.puntuacion.data,
            tipo_comentario=tipo_comentario,
            ciudad=request.remote_addr,  # Como ejemplo, se podría usar un servicio de geolocalización real
            direccion_ip=request.remote_addr,
            estrellitas='⭐' * form.puntuacion.data
        )

        # Actualizar contadores de comentarios en el producto
        if tipo_comentario == 'positivo':
            producto.comentarios_positivos += 1
        else:
            producto.comentarios_negativos += 1

        db.session.add(resena)
        db.session.commit()

        flash('Tu reseña ha sido publicada!', 'success')
    else:
        flash('Hubo un error al publicar tu reseña.', 'danger')

    return redirect(url_for('productos.ver_producto', producto_id=producto.id_producto))


@productos.route('/producto/<int:producto_id>/interaccion', methods=['POST'])
@login_required
def interactuar(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    tipo = request.form.get('tipo')

    if tipo not in ['like', 'dislike']:
        return jsonify({'error': 'Tipo de interacción inválido'}), 400

    # Verificar si ya existe una interacción del usuario con este producto
    interaccion = InteraccionProducto.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_producto=producto.id_producto
    ).first()

    # Valores actuales para devolver en la respuesta
    likes_nuevos = producto.likes
    dislikes_nuevos = producto.dislikes
    action = None

    if interaccion:
        # Si la interacción es del mismo tipo, eliminarla (toggle)
        if interaccion.tipo_interaccion == tipo:
            # Decrementar contador
            if tipo == 'like':
                producto.likes = max(0, producto.likes - 1)
                likes_nuevos = producto.likes
            else:
                producto.dislikes = max(0, producto.dislikes - 1)
                dislikes_nuevos = producto.dislikes

            db.session.delete(interaccion)
            action = 'removed'
        else:
            # Cambiar tipo de interacción
            # Actualizar contadores
            if tipo == 'like':
                producto.likes += 1
                producto.dislikes = max(0, producto.dislikes - 1)
                likes_nuevos = producto.likes
                dislikes_nuevos = producto.dislikes
            else:
                producto.dislikes += 1
                producto.likes = max(0, producto.likes - 1)
                likes_nuevos = producto.likes
                dislikes_nuevos = producto.dislikes

            interaccion.tipo_interaccion = tipo
            interaccion.fecha_interaccion = datetime.utcnow()
            action = 'changed'
    else:
        # Crear nueva interacción
        nueva_interaccion = InteraccionProducto(
            id_usuario=current_user.id_usuario,
            id_producto=producto.id_producto,
            tipo_interaccion=tipo
        )

        # Incrementar contador
        if tipo == 'like':
            producto.likes += 1
            likes_nuevos = producto.likes
        else:
            producto.dislikes += 1
            dislikes_nuevos = producto.dislikes

        db.session.add(nueva_interaccion)
        action = 'added'

    db.session.commit()

    return jsonify({
        'success': True,
        'action': action,
        'tipo': tipo,
        'likes': likes_nuevos,
        'dislikes': dislikes_nuevos
    })

@productos.route('/producto/<int:producto_id>/favorito', methods=['POST'])
@login_required
def toggle_favorito(producto_id):
    producto = Producto.query.get_or_404(producto_id)

    # Verificar si el producto ya está en favoritos
    favorito = Favorito.query.filter_by(
        id_usuario=current_user.id_usuario,
        id_producto=producto.id_producto
    ).first()

    if favorito:
        # Eliminar de favoritos
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'success': True, 'action': 'removed'})
    else:
        # Agregar a favoritos
        nuevo_favorito = Favorito(
            id_usuario=current_user.id_usuario,
            id_producto=producto.id_producto
        )
        db.session.add(nuevo_favorito)
        db.session.commit()
        return jsonify({'success': True, 'action': 'added'})