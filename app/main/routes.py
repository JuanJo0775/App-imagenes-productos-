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

    if query:
        # Buscar productos por nombre o descripción
        resultados = Producto.query.filter(
            Producto.nombre.contains(query) |
            Producto.descripcion.contains(query)
        ).order_by(
            desc(Producto.fecha_ingreso)
        ).paginate(
            page=page,
            per_page=12,
            error_out=False
        )
    else:
        resultados = Producto.query.paginate(
            page=page,
            per_page=12,
            error_out=False
        )

    return render_template(
        'buscar.html',
        title='Resultados de búsqueda',
        query=query,
        productos=resultados
    )