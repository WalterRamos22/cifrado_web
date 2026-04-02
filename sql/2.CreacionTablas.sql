--Crea la tabla de usuarios--
CREATE TABLE usuarios (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(100),
    correo VARCHAR(100) UNIQUE,
    password VARCHAR(100)
);

--Crea la tabla de textos--
CREATE TABLE textos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    texto_original VARCHAR(MAX),
    texto_cifrado VARCHAR(MAX),
    token VARCHAR(255) UNIQUE,
    fecha DATETIME,
    usuario_id INT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

--Crea la tabla historial--
CREATE TABLE historial (
    id INT IDENTITY(1,1) PRIMARY KEY,
    usuario_id INT,
    texto_id INT,
    token VARCHAR(255),
    fecha_consulta DATETIME,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    FOREIGN KEY (texto_id) REFERENCES textos(id)
);
