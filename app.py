from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta'
# --- CONTROLADOR DE CONEXIÓN ---
def get_db_connection():
    """ 
    Establece el enlace técnico con SQLite. 
    Se utiliza row_factory para mapear las columnas por nombre.
    """
    conexion = sqlite3.connect('founad.db')
    conexion.row_factory = sqlite3.Row
    return conexion

# --- RUTAS DE NAVEGACIÓN (VISTAS) ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro')
def registro():
    """Renderiza el módulo de registro de nuevos perfiles."""
    # Esta línea le dice a Flask que busque el archivo físico en /templates
    return render_template('registro.html')

@app.route('/proyectos')
def proyectos():
    return render_template('proyectos.html')

@app.route('/sube')
def sube():
    return render_template('sube.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
        usuario = cursor.fetchone()

        db.close()

        if usuario:
            if usuario['password'] == password:
                session['usuario'] = usuario['nombre']
            
                return redirect('/')
            else:
                return "Contraseña incorrecta ❌"
        else:
            return "Usuario no encontrado ❌"

    return render_template('login.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

# --- LÓGICA DE NEGOCIO / PROCESAMIENTO ---
@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    """
    Gestiona la persistencia de datos del formulario de registro.
    Aplica sentencias preparadas para mitigar riesgos de seguridad.
    """
    if request.method == 'POST':
        # Captura de parámetros desde el objeto request
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']

        try:
            # Apertura de sesión en la base de datos
            db = get_db_connection()
            cursor = db.cursor()
            
            # Operación DML (Data Manipulation Language)
            cursor.execute('''
                INSERT INTO usuarios (nombre, email, password, rol)
                VALUES (?, ?, ?, ?)
            ''', (nombre, email, password, rol))
            
            db.commit() # Consolidación de la transacción
            db.close()
            
            # Confirmación de proceso exitoso
            return "Registro exitoso. <a href='/'>Regresar al inicio</a>"
            
        except sqlite3.IntegrityError:
            # Manejo de excepción para correos duplicados (campo UNIQUE)
            return "Error: El correo ingresado ya se encuentra en nuestro sistema."
        except Exception as e:
            # Captura de errores genéricos para depuración
            return f"Error técnico detectado: {e}"
        
@app.route('/logout')
def logout():
    # Eliminamos el dato del usuario de la sesión
    session.pop('usuario', None)
    # Lo redirigimos a la página de inicio
    return redirect(url_for('index'))
        

        
        
        

if __name__ == '__main__':
    # Ejecución del servidor en el puerto 5001 según configuración previa
    app.run(debug=True, port=5001)