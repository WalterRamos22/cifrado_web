# IMPORTACIONES

from flask import Flask, render_template, request, redirect, session
# Flask: para crear la aplicación web
# render_template: para mostrar HTML
# request: para recibir datos de formularios
# redirect: para redirigir páginas
# session: para manejar sesiones de usuario


# Conexión a la base de datos (archivo db.py)
from db import conectar


# Librerías auxiliares
import uuid              # Para generar tokens únicos
import base64            # Para cifrado sencillo
from datetime import datetime  # Para fecha y hora


# CONFIGURACIÓN DE LA APP
app = Flask(__name__)


# Clave secreta para manejar sesiones
app.secret_key = "secreto123"


# FUNCIONES DE CIFRADO
# Esta función convierte texto a Base64 (cifrado sencillo)
def cifrar_texto(texto):
    return base64.b64encode(texto.encode()).decode()


# Esta función revierte el cifrado Base64
def descifrar_texto(texto_cifrado):
    return base64.b64decode(texto_cifrado).decode()


# LOGIN
# Permite al usuario iniciar sesión
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        password = request.form["password"]

        # Conectar a la BD
        conexion = conectar()
        cursor = conexion.cursor()

        # Buscar usuario
        cursor.execute(
            "SELECT * FROM usuarios WHERE correo=? AND password=?",
            (correo, password)
        )

        usuario = cursor.fetchone()
        conexion.close()

        # Si existe el usuario → guardar sesión
        if usuario:
            session["usuario_id"] = usuario[0]
            return redirect("/home")

    return render_template("login.html")


# REGISTRO
# Permite crear un nuevo usuario
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        password = request.form["password"]

        conexion = conectar()
        cursor = conexion.cursor()

        # Insertar usuario
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, password) VALUES (?, ?, ?)",
            (nombre, correo, password)
        )

        conexion.commit()
        conexion.close()

        return redirect("/")

    return render_template("registro.html")


# HOME
# Pantalla principal después de login
@app.route("/home")
def home():
    # Validar que el usuario esté logueado
    if "usuario_id" not in session:
        return redirect("/")
    return render_template("home.html")


# CIFRAR TEXTO
# Permite ingresar texto, cifrarlo y guardar en BD
@app.route("/cifrar", methods=["GET", "POST"])
def cifrar():
    # Validar sesión
    if "usuario_id" not in session:
        return redirect("/")

    if request.method == "POST":
        texto = request.form["texto"]

        # Cifrar texto
        texto_cifrado = cifrar_texto(texto)

        # Generar token único
        token = str(uuid.uuid4())

        # Obtener fecha actual
        fecha = datetime.now()

        # Guardar en base de datos
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "INSERT INTO textos (texto_original, texto_cifrado, token, fecha, usuario_id) VALUES (?, ?, ?, ?, ?)",
            (texto, texto_cifrado, token, fecha, session["usuario_id"])
        )

        conexion.commit()
        conexion.close()

        # Mostrar token al usuario
        return f"Texto cifrado correctamente 🔐<br>Token: {token}"

    return render_template("cifrar.html")


# DESCIFRAR POR TOKEN
@app.route("/descifrar", methods=["GET", "POST"])
def descifrar():
    if "usuario_id" not in session:
        return redirect("/")

    if request.method == "POST":
        token = request.form["token"]

        conexion = conectar()
        cursor = conexion.cursor()

        # Buscar el texto por token
        cursor.execute(
            "SELECT * FROM textos WHERE token=?",
            (token,)
        )

        texto = cursor.fetchone()

        if texto:
            texto_original = texto[1]
            texto_cifrado = texto[2]
            fecha = texto[4]
            texto_id = texto[0]

            # Descifrar
            texto_descifrado = descifrar_texto(texto_cifrado)

            # Guardar en historial
            cursor.execute(
                "INSERT INTO historial (usuario_id, texto_id, token, fecha_consulta) VALUES (?, ?, ?, ?)",
                (session["usuario_id"], texto_id, token, datetime.now())
            )

            conexion.commit()
            conexion.close()

            return f"""
            Texto original: {texto_original} <br>
            Texto descifrado: {texto_descifrado} <br>
            Fecha: {fecha}
            """

        conexion.close()
        return "Token no encontrado"

    return render_template("descifrar.html")


# HISTORIAL
@app.route("/historial")
def historial():
    if "usuario_id" not in session:
        return redirect("/")

    conexion = conectar()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT h.token, h.fecha_consulta
        FROM historial h
        WHERE h.usuario_id = ?
        ORDER BY h.fecha_consulta DESC
    """, (session["usuario_id"],))

    datos = cursor.fetchall()
    conexion.close()

    return render_template("historial.html", datos=datos)


# EJECUCIÓN DE LA APP
# Este bloque inicia el servidor Flask
if __name__ == "__main__":
    app.run(debug=True)
