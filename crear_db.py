import sqlite3

def crear_base():
    try:
        conn = sqlite3.connect('founad.db')
        cursor = conn.cursor()
        
        # 1. Limpieza total (Borramos todo para que no haya conflictos de versiones)
        cursor.execute('DROP TABLE IF EXISTS calificaciones')
        cursor.execute('DROP TABLE IF EXISTS avances')
        cursor.execute('DROP TABLE IF EXISTS donaciones')
        cursor.execute('DROP TABLE IF EXISTS proyectos')
        cursor.execute('DROP TABLE IF EXISTS usuarios')

        # 2. Tabla de Usuarios
        cursor.execute('''
            CREATE TABLE usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nombre TEXT, 
                email TEXT UNIQUE, 
                password TEXT, 
                rol TEXT
            )
        ''')

        # 3. Tabla de Proyectos (Con conexión al usuario creador)
        cursor.execute('''
            CREATE TABLE proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nombre TEXT, 
                descripcion TEXT, 
                categoria TEXT, 
                meta REAL, 
                fecha_limite TEXT, 
                archivo_ruta TEXT, 
                imagen_ruta TEXT, 
                video_url TEXT, 
                id_usuario INTEGER,
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        ''')

        # 4. Tabla de Donaciones
        cursor.execute('''
            CREATE TABLE donaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_proyecto INTEGER, 
                id_usuario INTEGER, 
                monto REAL, 
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos (id),
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        ''')

        # 5. Tabla de Avances (Muro de actualizaciones)
        cursor.execute('''
            CREATE TABLE avances (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_proyecto INTEGER, 
                mensaje TEXT, 
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos (id)
            )
        ''')

        # 6. NUEVA: Tabla de Calificaciones (Estrellas)
        cursor.execute('''
            CREATE TABLE calificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_proyecto INTEGER,
                id_usuario INTEGER,
                estrellas INTEGER,
                FOREIGN KEY (id_proyecto) REFERENCES proyectos (id),
                FOREIGN KEY (id_usuario) REFERENCES usuarios (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print(">>> EXITO: BASE DE DATOS FOUNAD CREADA CON CALIFICACIONES <<<")
    except Exception as e:
        print(f"ERROR: {e}")

# Ejecutar la creación
crear_base()