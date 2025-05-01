from flask import Blueprint, render_template, request
from app.models import Producto, Categoria
from app import db
from sqlalchemy import desc

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    categorias = Categoria.query.all()

    # Obtener productos destacados (los que tienen más likes)
    destacados = Producto.query.order_by(desc(Producto.likes)).limit(4).all()

    # Obtener productos paginados
    productos = Producto.query.order_by(
        desc(Producto.fecha_ingreso)
    ).paginate(
        page=page,
        per_page=12,
        error_out=False
    )

    return render_template(
        'index.html',
        title='Inicio',
        productos=productos,
        destacados=destacados,
        categorias=categorias
    )


@main.route('/buscar')
def buscar():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    categoria_id = request.args.get('categoria', type=int)
    ordenar = request.args.get('ordenar', 'fecha_desc')

    # Base query
    base_query = Producto.query

    # Filtrar por búsqueda
    if query:
        base_query = base_query.filter(
            Producto.nombre.contains(query) |
            Producto.descripcion.contains(query) |
            Producto.ficha_tecnica.contains(query)
        )

    # Filtrar por categoría
    if categoria_id:
        base_query = base_query.filter_by(id_categoria=categoria_id)

    # Ordenar resultados
    if ordenar == 'fecha_desc':
        base_query = base_query.order_by(desc(Producto.fecha_ingreso))
    elif ordenar == 'fecha_asc':
        base_query = base_query.order_by(Producto.fecha_ingreso)
    elif ordenar == 'likes_desc':
        base_query = base_query.order_by(desc(Producto.likes))
    elif ordenar == 'likes_asc':
        base_query = base_query.order_by(Producto.likes)
    elif ordenar == 'nombre_asc':
        base_query = base_query.order_by(Producto.nombre)
    elif ordenar == 'nombre_desc':
        base_query = base_query.order_by(desc(Producto.nombre))

    # Paginar los resultados
    resultados = base_query.paginate(
        page=page,
        per_page=12,
        error_out=False
    )

    # Obtener todas las categorías para el filtro
    categorias = Categoria.query.all()

    return render_template(
        'buscar.html',
        title='Resultados de búsqueda',
        query=query,
        productos=resultados,
        categorias=categorias,
        categoria_actual=categoria_id,
        ordenar=ordenar
    )