from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta'

# Configuración de carpetas para archivos
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Crear la carpeta de subidas si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- CONTROLADOR DE CONEXIÓN ---
def get_db_connection():
    conexion = sqlite3.connect('founad.db')
    conexion.row_factory = sqlite3.Row
    return conexion

# --- RUTAS DE NAVEGACIÓN Y USUARIOS ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        password = request.form['password']
        rol = request.form['rol']
        try:
            db = get_db_connection()
            db.execute('INSERT INTO usuarios (nombre, email, password, rol) VALUES (?, ?, ?, ?)',
                       (nombre, email, password, rol))
            db.commit()
            db.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            return "El correo ya está registrado. <a href='/registro'>Intentar de nuevo</a>"
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db_connection()
        usuario = db.execute('SELECT * FROM usuarios WHERE email = ?', (email,)).fetchone()
        db.close()
        if usuario and usuario['password'] == password:
            session['usuario'] = usuario['nombre']
            return redirect(url_for('index'))
        return "Credenciales incorrectas. <a href='/login'>Volver a intentar</a>"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('index'))

# --- GESTIÓN DE PROYECTOS (CRUD) ---

@app.route('/proyectos')
def proyectos():
    db = get_db_connection()
    
    # 1. Consulta principal (Subconsultas para evitar que desaparezcan proyectos)
    query = '''
    SELECT p.*, 
           u.nombre as nombre_usuario_creador,
           (SELECT IFNULL(SUM(monto), 0) FROM donaciones WHERE id_proyecto = p.id) as acumulado,
           (SELECT IFNULL(AVG(estrellas), 0) FROM calificaciones WHERE id_proyecto = p.id) as promedio_estrellas
    FROM proyectos p
    LEFT JOIN usuarios u ON p.id_usuario = u.id
    ORDER BY p.id DESC
    '''
    proyectos_data = db.execute(query).fetchall()
    
    lista_final = []
    for p in proyectos_data:
        proyecto_dict = dict(p)
        
        # 2. AQUÍ ESTABA EL ERROR: Usamos p['id'] para filtrar los avances
        avances = db.execute('''
            SELECT mensaje, fecha 
            FROM avances 
            WHERE id_proyecto = ? 
            ORDER BY fecha DESC
        ''', (p['id'],)).fetchall()
        
        proyecto_dict['lista_avances'] = avances
        lista_final.append(proyecto_dict)
        
    db.close()
    return render_template('proyectos.html', proyectos=lista_final)

@app.route('/sube')
def sube():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    return render_template('sube.html')

@app.route('/subir_proyecto', methods=['POST'])
def subir_proyecto():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    categoria = request.form['categoria']
    meta = request.form['meta']
    fecha_limite = request.form['fecha_limite']
    video_url = request.form.get('video', '')

    foto = request.files['imagen']
    archivo = request.files['archivo']
    foto_filename = secure_filename(foto.filename)
    archivo_filename = secure_filename(archivo.filename)

    foto.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
    archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo_filename))

    db = get_db_connection()
    user = db.execute('SELECT id FROM usuarios WHERE nombre = ?', (session['usuario'],)).fetchone()
    if user:
        db.execute('''
            INSERT INTO proyectos (nombre, descripcion, categoria, meta, fecha_limite, archivo_ruta, imagen_ruta, video_url, id_usuario)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, descripcion, categoria, meta, fecha_limite, archivo_filename, foto_filename, video_url, user['id']))
        db.commit()
    db.close()
    return redirect(url_for('proyectos'))

@app.route('/editar_proyecto/<int:id>', methods=['GET', 'POST'])
def editar_proyecto(id):
    db = get_db_connection()
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        meta = request.form['meta']
        db.execute('UPDATE proyectos SET nombre=?, descripcion=?, meta=? WHERE id=?', (nombre, descripcion, meta, id))
        db.commit()
        db.close()
        return redirect(url_for('proyectos'))
    
    proyecto = db.execute('SELECT * FROM proyectos WHERE id = ?', (id,)).fetchone()
    db.close()
    return render_template('editar.html', proyecto=proyecto)

@app.route('/eliminar_proyecto/<int:id>')
def eliminar_proyecto(id):
    db = get_db_connection()
    db.execute('DELETE FROM proyectos WHERE id = ?', (id,))
    db.commit()
    db.close()
    return redirect(url_for('proyectos'))

# --- DONACIONES Y AVANCES ---

@app.route('/donar/<int:proyecto_id>', methods=['POST'])
def donar(proyecto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    monto = request.form.get('monto')
    db = get_db_connection()
    user = db.execute('SELECT id FROM usuarios WHERE nombre = ?', (session['usuario'],)).fetchone()
    if user:
        db.execute('INSERT INTO donaciones (id_proyecto, id_usuario, monto) VALUES (?, ?, ?)',
                   (proyecto_id, user['id'], monto))
        db.commit()
    db.close()
    return redirect(url_for('proyectos'))

@app.route('/publicar_avance/<int:proyecto_id>', methods=['POST'])
def publicar_avance(proyecto_id):
    mensaje = request.form.get('mensaje')
    db = get_db_connection()
    db.execute('INSERT INTO avances (id_proyecto, mensaje) VALUES (?, ?)', (proyecto_id, mensaje))
    db.commit()
    db.close()
    return redirect(url_for('proyectos'))

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')


@app.route('/calificar/<int:proyecto_id>', methods=['POST'])
def calificar(proyecto_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    estrellas = request.form.get('estrellas')
    db = get_db_connection()
    user = db.execute('SELECT id FROM usuarios WHERE nombre = ?', (session['usuario'],)).fetchone()
    
    if user:
        # Registramos la calificación del usuario
        db.execute('INSERT INTO calificaciones (id_proyecto, id_usuario, estrellas) VALUES (?, ?, ?)',
                   (proyecto_id, user['id'], estrellas))
        db.commit()
    db.close()
    return redirect(url_for('proyectos'))


if __name__ == '__main__':
    app.run(debug=True, port=5001)