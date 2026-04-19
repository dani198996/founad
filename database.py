import sqlite3

def crear_tablas():
    # se importa sqlite3 para crear la base de datos 
    conexion = sqlite3.connect('founad.db')
    cursor = conexion.cursor()

    # Creamos la tabla de usuarios para el Caso de Uso 1 (Registro)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            rol TEXT NOT NULL
        )
    ''')

    conexion.commit()
    conexion.close()
    # ponermos un mensaje para indicar que la base de datos se ha creado correctamente
    print("base de datos creada")

if __name__ == '__main__':
    crear_tablas()