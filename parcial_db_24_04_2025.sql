-- Database creation script
CREATE DATABASE IF NOT EXISTS tienda_art_pinturas CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE tienda_art_pinturas;

-- Database options
SET character_set_client = utf8mb4;
SET character_set_connection = utf8mb4;
SET character_set_database = utf8mb4;
SET character_set_results = utf8mb4;
SET character_set_server = utf8mb4;
SET collation_connection = utf8mb4_general_ci;
SET collation_database = utf8mb4_general_ci;
SET collation_server = utf8mb4_general_ci;

-- Drop tables if they exist (in correct order to respect foreign key constraints)
DROP TABLE IF EXISTS favoritos;
DROP TABLE IF EXISTS imagenes_producto;
DROP TABLE IF EXISTS videos_producto;
DROP TABLE IF EXISTS interacciones_producto;
DROP TABLE IF EXISTS resenas;
DROP TABLE IF EXISTS imagenes_categoria;
DROP TABLE IF EXISTS productos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;

-- Create tables in the correct order
CREATE TABLE usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  nombre_usuario VARCHAR(100) NOT NULL,
  email VARCHAR(255) NOT NULL UNIQUE,
  contrasena VARCHAR(255) NOT NULL,
  fecha_registro DATETIME NOT NULL,
  es_admin TINYINT(1) DEFAULT 0,
  UNIQUE INDEX email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE categorias (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nombre_categoria VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE productos (
  id_producto INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(255) NOT NULL,
  descripcion TEXT,
  ficha_tecnica TEXT,
  fecha_ingreso DATE DEFAULT CURDATE(),
  id_categoria INT NOT NULL,
  likes INT DEFAULT 0,
  dislikes INT DEFAULT 0,
  comentarios_positivos INT DEFAULT 0,
  comentarios_negativos INT DEFAULT 0,
  CONSTRAINT fk_categoria FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE favoritos (
  id_usuario INT NOT NULL,
  id_producto INT NOT NULL,
  fecha_agregado DATETIME NOT NULL,
  PRIMARY KEY (id_usuario, id_producto),
  CONSTRAINT fk_producto_favorito FOREIGN KEY (id_producto) REFERENCES productos (id_producto),
  CONSTRAINT fk_usuario_favorito FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE imagenes_categoria (
  id_imagen_categoria INT AUTO_INCREMENT PRIMARY KEY,
  id_categoria INT NOT NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  ruta_archivo VARCHAR(255) NOT NULL,
  fecha_subida DATETIME NOT NULL,
  CONSTRAINT fk_categoria_imagen FOREIGN KEY (id_categoria) REFERENCES categorias (id_categoria)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE imagenes_producto (
  id_imagen INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  ruta_archivo VARCHAR(255) NOT NULL,
  fecha_subida DATETIME NOT NULL,
  CONSTRAINT fk_producto_imagen FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE interacciones_producto (
  id_usuario INT NOT NULL,
  id_producto INT NOT NULL,
  tipo_interaccion ENUM('like', 'dislike') NOT NULL,
  fecha_interaccion DATETIME NOT NULL,
  PRIMARY KEY (id_usuario, id_producto),
  CONSTRAINT fk_producto_interaccion FOREIGN KEY (id_producto) REFERENCES productos (id_producto),
  CONSTRAINT fk_usuario_interaccion FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE resenas (
  id_resena INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  id_usuario INT NOT NULL,
  comentario TEXT NOT NULL,
  puntuacion INT NOT NULL,
  tipo_comentario ENUM('positivo', 'negativo'),
  ciudad VARCHAR(100),
  direccion_ip VARCHAR(45),
  fecha_hora DATETIME NOT NULL,
  estrellitas INT,
  CONSTRAINT fk_producto FOREIGN KEY (id_producto) REFERENCES productos (id_producto),
  CONSTRAINT fk_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios (id_usuario),
  CHECK (puntuacion BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE videos_producto (
  id_video INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  nombre_archivo VARCHAR(255) NOT NULL,
  ruta_archivo VARCHAR(255) NOT NULL,
  fecha_subida DATETIME NOT NULL,
  CONSTRAINT fk_producto_video FOREIGN KEY (id_producto) REFERENCES productos (id_producto)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;