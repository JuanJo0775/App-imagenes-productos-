from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app, abort
from flask_login import login_required, current_user
from app import db
from app.models import Usuario, Producto, Categoria, ImagenProducto, VideoProducto, ImagenCategoria, Resena
from app.admin.forms import (
    ProductoForm, CategoriaForm, ImagenProductoForm,
    VideoProductoForm, ImagenCategoriaForm
)
from werkzeug.utils import secure_filename
import os
from functools import wraps
import uuid
from datetime import datetime
from sqlalchemy import desc

admin = Blueprint('admin', __name__)


# Función para verificar si el usuario es administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Por ahora, consideraremos como "admin" al usuario con ID 1
        # En un sistema real, tendríamos un campo de rol en la tabla de usuarios
        if not current_user.is_authenticated or current_user.id_usuario != 1:
            abort(403)  # Forbidden
        return f(*args, **kwargs)

    return decorated_function


# Función auxiliar para guardar archivos
def guardar_archivo(archivo, tipo):
    if archivo.filename == '':
        return None

    filename = secure_filename(archivo.filename)
    # Agregar timestamp al nombre para evitar colisiones
    filename = f"{uuid.uuid4().hex}_{filename}"

    if tipo == 'imagen_producto':
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos/imagenes', filename)
    elif tipo == 'video_producto':
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'productos/videos', filename)
    elif tipo == 'imagen_categoria':
        ruta = os.path.join(current_app.config['UPLOAD_FOLDER'], 'categorias/imagenes', filename)

    # Asegurarse de que el directorio exista
    os.makedirs(os.path.dirname(ruta), exist_ok=True)

    # Guardar el archivo
    archivo.save(ruta)

    # Devolver la ruta relativa para almacenar en la base de datos
    return os.path.join(tipo.replace('_', '/'), filename)


@admin.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Contar productos, categorías y usuarios
    total_productos = Producto.query.count()
    total_categorias = Categoria.query.count()
    total_usuarios = Usuario.query.count()
    total_resenas = Resena.query.count()

    # Obtener productos recientes
    productos_recientes = Producto.query.order_by(desc(Producto.fecha_ingreso)).limit(5).all()

    # Obtener usuarios recientes
    usuarios_recientes = Usuario.query.order_by(desc(Usuario.fecha_registro)).limit(5).all()

    return render_template(
        'admin/dashboard.html',
        title='Panel de Administración',
        total_productos=total_productos,
        total_categorias=total_categorias,
        total_usuarios=total_usuarios,
        total_resenas=total_resenas,
        productos_recientes=productos_recientes,
        usuarios_recientes=usuarios_recientes
    )


# Rutas para gestión de productos
@admin.route('/productos')
@login_required
@admin_required
def listar_productos():
    page = request.args.get('page', 1, type=int)
    productos = Producto.query.order_by(desc(Producto.fecha_ingreso)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template(
        'admin/productos/listar.html',
        title='Administrar Productos',
        productos=productos
    )


@admin.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_producto():
    form = ProductoForm()
    # Obtener categorías para el select field
    form.id_categoria.choices = [(c.id_categoria, c.nombre_categoria)
                                 for c in Categoria.query.order_by('nombre_categoria')]

    if form.validate_on_submit():
        producto = Producto(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            ficha_tecnica=form.ficha_tecnica.data,
            id_categoria=form.id_categoria.data
        )
        db.session.add(producto)
        db.session.commit()

        flash('Producto creado con éxito!', 'success')
        return redirect(url_for('admin.listar_productos'))

    return render_template(
        'admin/productos/formulario.html',
        title='Nuevo Producto',
        form=form,
        legend='Nuevo Producto'
    )


@admin.route('/productos/<int:producto_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ProductoForm()
    form.id_categoria.choices = [(c.id_categoria, c.nombre_categoria)
                                 for c in Categoria.query.order_by('nombre_categoria')]

    if form.validate_on_submit():
        producto.nombre = form.nombre.data
        producto.descripcion = form.descripcion.data
        producto.ficha_tecnica = form.ficha_tecnica.data
        producto.id_categoria = form.id_categoria.data

        db.session.commit()
        flash('Producto actualizado con éxito!', 'success')
        return redirect(url_for('admin.listar_productos'))
    elif request.method == 'GET':
        form.nombre.data = producto.nombre
        form.descripcion.data = producto.descripcion
        form.ficha_tecnica.data = producto.ficha_tecnica
        form.id_categoria.data = producto.id_categoria

    return render_template(
        'admin/productos/formulario.html',
        title='Editar Producto',
        form=form,
        legend='Editar Producto',
        producto=producto
    )


@admin.route('/productos/<int:producto_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado con éxito!', 'success')
    return redirect(url_for('admin.listar_productos'))


@admin.route('/productos/<int:producto_id>/imagenes', methods=['GET', 'POST'])
@login_required
@admin_required
def administrar_imagenes_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = ImagenProductoForm()

    if form.validate_on_submit():
        archivo = form.imagen.data
        if archivo:
            ruta_archivo = guardar_archivo(archivo, 'imagen_producto')
            if ruta_archivo:
                imagen = ImagenProducto(
                    id_producto=producto.id_producto,
                    nombre_archivo=form.nombre.data or archivo.filename,
                    ruta_archivo=ruta_archivo
                )
                db.session.add(imagen)
                db.session.commit()
                flash('Imagen agregada con éxito!', 'success')
                return redirect(url_for('admin.administrar_imagenes_producto', producto_id=producto.id_producto))

    imagenes = ImagenProducto.query.filter_by(id_producto=producto_id).all()

    return render_template(
        'admin/productos/imagenes.html',
        title=f'Administrar Imágenes - {producto.nombre}',
        producto=producto,
        form=form,
        imagenes=imagenes
    )


@admin.route('/productos/<int:producto_id>/videos', methods=['GET', 'POST'])
@login_required
@admin_required
def administrar_videos_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    form = VideoProductoForm()

    if form.validate_on_submit():
        archivo = form.video.data
        if archivo:
            ruta_archivo = guardar_archivo(archivo, 'video_producto')
            if ruta_archivo:
                video = VideoProducto(
                    id_producto=producto.id_producto,
                    nombre_archivo=form.nombre.data or archivo.filename,
                    ruta_archivo=ruta_archivo
                )
                db.session.add(video)
                db.session.commit()
                flash('Video agregado con éxito!', 'success')
                return redirect(url_for('admin.administrar_videos_producto', producto_id=producto.id_producto))

    videos = VideoProducto.query.filter_by(id_producto=producto_id).all()

    return render_template(
        'admin/productos/videos.html',
        title=f'Administrar Videos - {producto.nombre}',
        producto=producto,
        form=form,
        videos=videos
    )


# Rutas para gestión de categorías
@admin.route('/categorias')
@login_required
@admin_required
def listar_categorias():
    page = request.args.get('page', 1, type=int)
    categorias = Categoria.query.order_by('nombre_categoria').paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template(
        'admin/categorias/listar.html',
        title='Administrar Categorías',
        categorias=categorias
    )


@admin.route('/categorias/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_categoria():
    form = CategoriaForm()

    if form.validate_on_submit():
        categoria = Categoria(
            nombre_categoria=form.nombre_categoria.data
        )
        db.session.add(categoria)
        db.session.commit()

        flash('Categoría creada con éxito!', 'success')
        return redirect(url_for('admin.listar_categorias'))

    return render_template(
        'admin/categorias/formulario.html',
        title='Nueva Categoría',
        form=form,
        legend='Nueva Categoría'
    )


@admin.route('/categorias/<int:categoria_id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    form = CategoriaForm()

    if form.validate_on_submit():
        categoria.nombre_categoria = form.nombre_categoria.data
        db.session.commit()
        flash('Categoría actualizada con éxito!', 'success')
        return redirect(url_for('admin.listar_categorias'))
    elif request.method == 'GET':
        form.nombre_categoria.data = categoria.nombre_categoria

    return render_template(
        'admin/categorias/formulario.html',
        title='Editar Categoría',
        form=form,
        legend='Editar Categoría'
    )


@admin.route('/categorias/<int:categoria_id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    db.session.delete(categoria)
    db.session.commit()
    flash('Categoría eliminada con éxito!', 'success')
    return redirect(url_for('admin.listar_categorias'))


@admin.route('/categorias/<int:categoria_id>/imagenes', methods=['GET', 'POST'])
@login_required
@admin_required
def administrar_imagenes_categoria(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    form = ImagenCategoriaForm()

    if form.validate_on_submit():
        archivo = form.imagen.data
        if archivo:
            ruta_archivo = guardar_archivo(archivo, 'imagen_categoria')
            if ruta_archivo:
                imagen = ImagenCategoria(
                    id_categoria=categoria.id_categoria,
                    nombre_archivo=form.nombre.data or archivo.filename,
                    ruta_archivo=ruta_archivo
                )
                db.session.add(imagen)
                db.session.commit()
                flash('Imagen agregada con éxito!', 'success')
                return redirect(url_for('admin.administrar_imagenes_categoria', categoria_id=categoria.id_categoria))

    imagenes = ImagenCategoria.query.filter_by(id_categoria=categoria_id).all()

    return render_template(
        'admin/categorias/imagenes.html',
        title=f'Administrar Imágenes - {categoria.nombre_categoria}',
        categoria=categoria,
        form=form,
        imagenes=imagenes
    )


# Rutas para gestión de usuarios (administrador)
@admin.route('/usuarios')
@login_required
@admin_required
def listar_usuarios():
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.order_by(desc(Usuario.fecha_registro)).paginate(
        page=page, per_page=10, error_out=False
    )
    return render_template(
        'admin/usuarios/listar.html',
        title='Administrar Usuarios',
        usuarios=usuarios
    )


@admin.route('/usuarios/<int:usuario_id>/detalle')
@login_required
@admin_required
def detalle_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    # Obtener número de reseñas
    num_resenas = Resena.query.filter_by(id_usuario=usuario_id).count()
    # Obtener número de favoritos
    num_favoritos = Favorito.query.filter_by(id_usuario=usuario_id).count()

    return render_template(
        'admin/usuarios/detalle.html',
        title=f'Usuario: {usuario.nombre_usuario}',
        usuario=usuario,
        num_resenas=num_resenas,
        num_favoritos=num_favoritos
    )