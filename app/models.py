from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Categoria(db.Model):
    __tablename__ = 'categorias'
    id_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(100), nullable=False)

    # Relaciones
    productos = db.relationship('Producto', backref='categoria', lazy=True)
    imagenes = db.relationship('ImagenCategoria', backref='categoria', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Categoria('{self.nombre_categoria}')"


class Producto(db.Model):
    __tablename__ = 'productos'
    id_producto = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    ficha_tecnica = db.Column(db.Text)
    fecha_ingreso = db.Column(db.Date, default=datetime.utcnow().date)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria', ondelete='SET NULL'))
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    comentarios_positivos = db.Column(db.Integer, default=0)
    comentarios_negativos = db.Column(db.Integer, default=0)

    # Relaciones
    imagenes = db.relationship('ImagenProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    videos = db.relationship('VideoProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    resenas = db.relationship('Resena', backref='producto', lazy=True, cascade="all, delete-orphan")
    interacciones = db.relationship('InteraccionProducto', backref='producto', lazy=True, cascade="all, delete-orphan")
    favoritos = db.relationship('Favorito', backref='producto', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"Producto('{self.nombre}')"


class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_usuario = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    resenas = db.relationship('Resena', backref='usuario', lazy=True)
    interacciones = db.relationship('InteraccionProducto', backref='usuario', lazy=True, cascade="all, delete-orphan")
    favoritos = db.relationship('Favorito', backref='usuario', lazy=True, cascade="all, delete-orphan")

    # Sobrescribir el método get_id para compatibilidad con Flask-Login
    def get_id(self):
        return str(self.id_usuario)

    def __repr__(self):
        return f"Usuario('{self.nombre_usuario}', '{self.email}')"


class Resena(db.Model):
    __tablename__ = 'resenas'
    id_resena = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='SET NULL'))
    comentario = db.Column(db.Text)
    puntuacion = db.Column(db.Integer, nullable=False)
    tipo_comentario = db.Column(db.Enum('positivo', 'negativo'), nullable=False)
    ciudad = db.Column(db.String(100))
    direccion_ip = db.Column(db.String(45))
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    estrellitas = db.Column(db.String(5))

    def __repr__(self):
        return f"Resena(Producto: {self.id_producto}, Usuario: {self.id_usuario}, Puntuación: {self.puntuacion})"


class ImagenProducto(db.Model):
    __tablename__ = 'imagenes_producto'
    id_imagen = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ImagenProducto('{self.nombre_archivo}')"


class VideoProducto(db.Model):
    __tablename__ = 'videos_producto'
    id_video = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"VideoProducto('{self.nombre_archivo}')"


class ImagenCategoria(db.Model):
    __tablename__ = 'imagenes_categoria'
    id_imagen_categoria = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria', ondelete='CASCADE'), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"ImagenCategoria('{self.nombre_archivo}')"


class InteraccionProducto(db.Model):
    __tablename__ = 'interacciones_producto'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), primary_key=True)
    tipo_interaccion = db.Column(db.Enum('like', 'dislike'), nullable=False)
    fecha_interaccion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"InteraccionProducto(Usuario: {self.id_usuario}, Producto: {self.id_producto}, Tipo: {self.tipo_interaccion})"


class Favorito(db.Model):
    __tablename__ = 'favoritos'
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario', ondelete='CASCADE'), primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('productos.id_producto', ondelete='CASCADE'), primary_key=True)
    fecha_agregado = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Favorito(Usuario: {self.id_usuario}, Producto: {self.id_producto})"