from app import create_app, db
from app.models import Usuario
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# Crear contexto de aplicación
app = create_app()

with app.app_context():
    # Verificar si la columna ya existe
    inspector = reflection.Inspector.from_engine(db.engine)
    columns = [c['name'] for c in inspector.get_columns('usuarios')]

    if 'es_admin' not in columns:
        print("Agregando columna 'es_admin' a la tabla 'usuarios'...")
        # Agregar la columna
        db.engine.execute('ALTER TABLE usuarios ADD COLUMN es_admin BOOLEAN DEFAULT FALSE')

        # Convertir el usuario 1 en admin
        admin = Usuario.query.get(1)
        if admin:
            admin.es_admin = True
            db.session.commit()
            print(f"Usuario '{admin.nombre_usuario}' actualizado como administrador.")
        else:
            print("No se encontró el usuario con ID 1. Asegúrate de crear un usuario admin.")

        print("Migración completada con éxito!")
    else:
        print("La columna 'es_admin' ya existe en la tabla 'usuarios'.")