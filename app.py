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
    # Usamos la función de conexión que ya tienes definida arriba
    db = get_db_connection()
    cursor = db.cursor()
    
    # 1. Traemos los proyectos con su acumulado de donaciones
    query = '''
    SELECT p.*, IFNULL(SUM(d.monto), 0) as acumulado
    FROM proyectos p
    LEFT JOIN donaciones d ON p.id = d.id_proyecto
    GROUP BY p.id
    '''
    proyectos_data = cursor.execute(query).fetchall()

    # 2. PROCESAMIENTO CRÍTICO: Creamos la lista que espera el HTML
    lista_final = []
    for p in proyectos_data:
        # Convertimos el objeto Row a un diccionario para poder agregarle datos
        proyecto_dict = dict(p)
        
        # Buscamos los avances específicos de este proyecto
        avances = cursor.execute('''
            SELECT mensaje, fecha 
            FROM avances 
            WHERE id_proyecto = ? 
            ORDER BY fecha DESC
        ''', (p['id'],)).fetchall()
        
        # Guardamos la lista de avances dentro del diccionario del proyecto
        # Esto es lo que el HTML lee como proyecto['lista_avances']
        proyecto_dict['lista_avances'] = avances
        
        lista_final.append(proyecto_dict)

    db.close()
    
    # IMPORTANTE: Enviamos lista_final al template
    return render_template('proyectos.html', proyectos=lista_final)
    db.close()
    return render_template('proyectos.html', proyectos=proyectos_lista)
    

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


import os
from werkzeug.utils import secure_filename

# Configuración de carpetas para archivos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/subir_proyecto', methods=['POST'])
def subir_proyecto():
    if request.method == 'POST':
        # Capturamos los datos del formulario
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        categoria = request.form['categoria']
        meta = request.form['meta']
        fecha_limite = request.form['fecha_limite']
        video_url = request.form.get('video', '')

        # Manejo de archivos (Imagen y PDF)
        foto = request.files['imagen']
        archivo = request.files['archivo']

        foto_filename = secure_filename(foto.filename)
        archivo_filename = secure_filename(archivo.filename)

        # Guardamos los archivos físicamente
        foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_filename))

        # Guardamos la información en la base de datos
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO proyectos (nombre, descripcion, categoria, meta, fecha_limite, archivo_ruta, imagen_ruta, video_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, descripcion, categoria, meta, fecha_limite, archivo_filename, foto_filename, video_url))
        
        db.commit()
        db.close()

        return "¡Proyecto publicado con éxito! 🎉 <a href='/proyectos'>Ver proyectos</a>"
        

@app.route('/donar/<int:proyecto_id>', methods=['POST'])
def donar(proyecto_id):
    # 1. Verificar si el usuario inició sesión
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    monto = request.form.get('monto')
    usuario_nombre = session['usuario']

    try:
        db = sqlite3.connect('founad.db')
        cursor = db.cursor()
        
        # 2. Buscamos el ID del usuario que está logueado
        cursor.execute('SELECT id FROM usuarios WHERE nombre = ?', (usuario_nombre,))
        usuario = cursor.fetchone()
        
        if usuario:
            # 3. Insertamos la donación en la tabla
            cursor.execute('INSERT INTO donaciones (id_proyecto, id_usuario, monto) VALUES (?, ?, ?)',
                           (proyecto_id, usuario[0], monto))
            db.commit()
            print(f"✅ ¡Éxito! Donación de {monto} para el proyecto ID {proyecto_id}")
        
        db.close()
    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")
    
    # 4. Volvemos a la lista de proyectos para ver el cambio
    return redirect(url_for('proyectos'))


@app.route('/publicar_avance/<int:proyecto_id>', methods=['POST'])
def publicar_avance(proyecto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    mensaje = request.form.get('mensaje')
    
    db = sqlite3.connect('founad.db')
    db.execute('INSERT INTO avances (id_proyecto, mensaje) VALUES (?, ?)', (proyecto_id, mensaje))
    db.commit()
    db.close()
    
    return redirect(url_for('proyectos'))
        
        
        

if __name__ == '__main__':
    # Ejecución del servidor en el puerto 5001 según configuración previa
    app.run(debug=True, port=5001)