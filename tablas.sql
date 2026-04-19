CREATE TABLE proyectos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    descripcion TEXT NOT NULL,
    categoria TEXT NOT NULL,
    meta REAL NOT NULL,
    fecha_limite TEXT NOT NULL,
    archivo_ruta TEXT,
    imagen_ruta TEXT,
    video_url TEXT
);