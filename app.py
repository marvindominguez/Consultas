from tempfile import template
from MySQLdb.cursors import Cursor
from xml.sax.handler import feature_external_ges
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask.wrappers import Request
from flask_mysqldb import MySQL
from datetime import date, datetime, timedelta
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Rolex.b1'
app.config['MYSQL_DB'] = 'consultas_iub'


mysql = MySQL(app)
app.secret_key = 'ghjklñ'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/index')  # login Psicologo
def index():
    return render_template('admin/login.html')


@app.route('/index_user')
def index_user():
    return render_template('index.html')


@app.route('/base')
def base():
    return render_template('admin/home.html')


@app.route('/index_admin')
def index_admin():
    # cursor = mysql.connection.cursor()
    # cursor.execute("SELECT r.id_caso, r.semaforo, r.observacion, r.documento, r.nombre, r.apellido, r.curso, r.edad, r.fecha_caso, r.genero, l.nombre FROM r_caso r INNER JOIN login_profesor l ON r.id_profesor = l.id_profesor")
    # casos = cursor.fetchall()
    # print(casos)
    # cursor.execute("SELECT fecha_nacimiento FROM estudiante")
    # fecha_nac = cursor.fetchone()[0]
    # hoy = date.today()
    # edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) <(fecha_nac.month, fecha_nac.day))
    # print(edad)
    return render_template('admin/index.html')


@app.route('/login_profe') #Login_Profe_URL
def login_profe():
    return render_template('profesor/login.html')



@app.route('/login_est') #Login_Est_URL
def login_est():
    return render_template('estudiante/login.html')


@app.route('/index_profe') 
def index_profe():
    users = session['id']
    print(users)    
    return render_template('profesor/index.html')


@app.route('/register')  # Registrar profesor
def register():
    datos = ['', '', '', '']
    return render_template('admin/register.html', datos=datos)


@app.route('/register_caso')  # Redireccionar Caso
def register_caso():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM modulo")
    modulo = cursor.fetchall()
    cursor.close()
    curs = mysql.connection.cursor()
    curs.execute("SELECT * FROM profesor")
    profesor = curs.fetchall()
    curs.close()
    return render_template('estudiante/register.html', modulo= modulo, profesor= profesor)
    
    
@app.route('/index_est')
def index_est():
    id = session['id']
    print(id)
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT estudiante.nombre AS nombre_estudiante, estudiante.apellido AS apellido_estudiante, estudiante.tipo_documento, estudiante.numero_estudiante, profesor.nombre AS nombre_profesor, estudiante.correo, modulo.nombre_modulo, estudiante.programa FROM estudiante INNER JOIN consulta ON estudiante.id = consulta.id_estudiante INNER JOIN profesor ON profesor.id = consulta.id_profesor INNER JOIN modulo ON modulo.id_modulo = consulta.id_modulo WHERE id_estudiante=%s',(id,))
    modulo = cursor.fetchall()
    return render_template('estudiante/index.html', modulo = modulo)


@app.route('/update_profile')
def update_profile():
    return render_template('estudiante/update_profile.html')



@app.route('/login', methods=['POST'])
def login():
    msg = ''
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM estudiante WHERE correo = %s AND contraseña = %s', (correo, contraseña))
        user = cursor.fetchone()
        print(user)
        if user:

            return redirect(url_for('index_admin'))
        else:
            msg = 'Los datos ingresados son incorrectos'
            return render_template('admin/login.html', msg=msg)


@app.route('/login_p', methods=['POST']) #Login_Profesor
def login_p():
    msg = ''
    if request.method == 'POST':
        documentop = request.form['documento']
        contraseñap = request.form['contraseña']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM profesor WHERE correo = %s AND password = %s', (documentop, contraseñap))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['nombre'] = user[1]
            session['apellido'] = user[2]
            session['correo'] = user[3]
            return redirect(url_for('index_profe'))
        else:
            msg = 'Los datos ingresados son incorrectos'
            return render_template('profesor/login.html', msg=msg)
        

@app.route('/login_estu', methods=['POST'])
def login_estu():
    if request.method == 'POST':
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'SELECT * FROM estudiante WHERE correo = %s AND contraseña = %s', (correo, contraseña))
        user = cursor.fetchone()
        # print(user)
        if user:
            session['loggedin'] = True
            session['id'] = user[0]
            session['nombre'] = user[1]
            session['apellido'] = user[2]
            session['correo'] = user[5]
            id = session['id']
            print(id)
            return redirect(url_for('index_est'))
            
            
        else:
            msg = 'Los datos ingresados son incorrectos'
            return render_template('estudiante/login.html', msg=msg)

        
@app.route('/ver_casos')
def ver_casos():
    # user = session['identificacion']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM profesor")
    v_casos = cursor.fetchall()
    return render_template('profesor/ver_casos.html', v_casos = v_casos)


@app.route('/res_cons', methods=['POST']) #Registrar Consulta estudiante
def res_cons():
    user = session['id']
    print(user)
    if request.method == 'POST':
        profesor = request.form['profesor']
        modulo = request.form['modulo']
        consulta = request.form['consulta']
        fecha = request.form['fecha']
        cons = mysql.connection.cursor()
        cons.execute('SELECT * FROM profesor WHERE nombre = %s', [str(profesor)])
        result = cons.fetchone()
        if result:
            id_profesor = result[0]
            print(id_profesor)
        cons.close()
        con = mysql.connection.cursor()
        con.execute('SELECT * FROM modulo WHERE nombre_modulo = %s', [str(modulo)])
        res = con.fetchone()
        if res:
            global id_modulo
            id_modulo = res[0]
            print(id_modulo)
        con.close()
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO consulta (id_estudiante, id_profesor, fecha, descripcion, id_modulo) VALUES (%s, %s, %s, %s, %s)',(user, id_profesor, fecha, consulta, id_modulo))
        mysql.connection.commit()
        cur.close()
        msg = 'La consulta se ha realizado correctamente!'
    return redirect(url_for('index_est', msg=msg))

        




# Cerrar sesion
@app.route('/logout')
def logout():
    # removemos los datos de la sesión para cerrar sesión
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('nombre', None)
    session.pop('apellido', None)
    session.pop('correo', None)
    session.pop('password', None)
    session.clear()
    return redirect(url_for('index'))


def status_401(error):
    return render_template('login')


def status_404(error):
    return '<h1>Página no encontrada</h1>', 404


if __name__ == '__main__':
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    # login_manager.init_app(app)
    app.run(port=5000, debug=True)
