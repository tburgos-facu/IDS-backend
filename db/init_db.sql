-- deportes
CREATE TABLE deportes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

INSERT INTO deportes (nombre) VALUES 
('Futbol'), 
('Tenis'), 
('Padel');

-- canchas
CREATE TABLE canchas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL,
    techada BOOLEAN DEFAULT FALSE,
    activa BOOLEAN DEFAULT TRUE
);

-- socios
CREATE TABLE socios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(254) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- reservas
CREATE TABLE reservas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cancha INT NOT NULL,
    id_socio INT NOT NULL,
    fecha_hora_inicio DATETIME(6),
    fecha_hora_fin DATETIME(6),
    estado VARCHAR(50),
    precio_hora INT NOT NULL,
    precio_total INT NOT NULL
);
