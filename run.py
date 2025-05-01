from app import create_app
from app.models import Categoria
from flask import g, request

app = create_app()

# Cargar las categorías disponibles para todos los templates
@app.before_request
def cargar_categorias():
    # Ignorar rutas de archivos estáticos
    if not request.path.startswith('/static'):
        g.categorias = Categoria.query.order_by(Categoria.nombre_categoria).all()

# Filtro personalizado para convertir saltos de línea en <br>
@app.template_filter('nl2br')
def nl2br(value):
    if value:
        return value.replace('\n', '<br>')
    return ''

if __name__ == '__main__':
    app.run(debug=True)