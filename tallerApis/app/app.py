from flask import Flask, request, jsonify
import psycopg2
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from random import choices
from string import ascii_letters, digits
from datetime import datetime, timedelta

app = Flask(__name__)
# Configuración del JWT
app.config['JWT_SECRET_KEY'] = 'mypass'
jwt = JWTManager(app)

# Almacén temporal para guardar los tokens de recuperación
reset_tokens = {}

# Configuración de la base de datos
db_config = {
    'dbname': 'authentication_db',
    'user': 'admin',
    'password': 'admin_password',
    'host': 'auth_postgres'
}

#--------------------------------------LOGIN-------------------------------------
@app.route('/inicio_sesion', methods=['POST'])
def inicio_sesion():
    # Establecer una conexión con la base de datos PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Obtener los datos del inicio de sesión desde la carga JSON de la solicitud HTTP
    data = request.get_json()
    email = data['email']
    password = data['password']

    # Buscar al usuario en la base de datos por su email
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user[2] == password:  # Verificar contraseña (esto debe ser un hash en la vida real)
        # Generar un token JWT
        access_token = create_access_token(identity=email)

        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        return jsonify({"Token de acceso": access_token}), 200
    else:
        # Cerrar el cursor y la conexión
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Credenciales invalidas"}), 401

#--------------------------------------CAMBIAR CONTRASEÑA------------------------
@app.route('/cambio_contrasena', methods=['POST'])
@jwt_required()
def cambio_contrasena():
    # Obtener la identidad del usuario desde el token JWT
    current_user_email = get_jwt_identity()

    # Establecer una conexión con la base de datos PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Obtener los datos de la nueva contraseña desde la carga JSON de la solicitud HTTP
    data = request.get_json()
    new_password = data['new_password']

    # Actualizar la contraseña del usuario en la base de datos
    cursor.execute("UPDATE users SET hashed_password = %s WHERE email = %s",
                   (new_password, current_user_email))

    # Confirmar la transacción y cerrar el cursor y la conexión
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Contrasena actualizada exitosamente"}), 200
    


#--------------------------------------RECUPERAR CLAVE---------------------------
# Ruta para solicitar recuperación de contraseña
@app.route('/recuperacion_contra', methods=['POST'])
def recuperacion_contrasena():
    # Obtener el correo electrónico proporcionado por el usuario
    data = request.get_json()
    email = data['email']

    # Generar un token de recuperación de contraseña
    reset_token = ''.join(choices(ascii_letters + digits, k=20))
    # Le da un tiempo al token
    expiration_time = datetime.now() + timedelta(minutes=30)
    reset_tokens[email] = {'token': reset_token, 'expiration_time': expiration_time}
    # reset_token  # Almacenar el token en el almacén temporal

    # En un escenario real, se debería enviar un correo electrónico con un enlace que contenga el token
    # Aquí solo mostramos el token generado para fines de demostración
    return jsonify({"mensaje": "Se ha generado un token de recuperacion", "token": reset_token}), 200

@app.route('/restablecemiento_contra', methods=['POST'])
def restablecemiento_contrasena():
    data = request.get_json()
    email = data['email']
    new_password = data['new_password']
    reset_token = data['reset_token']

    # Verificar si el token coincide con el token almacenado
    if email in reset_tokens:
        token_info = reset_tokens[email]
        token = token_info['token']
        expiration_time = token_info['expiration_time']

        if token == reset_token and expiration_time > datetime.now():
            # Se actualizaría la contraseña en la base de datos
            # Establecer una conexión con la base de datos PostgreSQL
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Actualizar la contraseña en la base de datos (esto es una simulación)
            cursor.execute("UPDATE users SET hashed_password = %s WHERE email = %s", (new_password, email))
            conn.commit()

            # Cerrar el cursor y la conexión
            cursor.close()
            conn.close()
            del reset_tokens[email]  # Eliminar el token después de su uso
            return jsonify({"mensaje": "Contrasena actualizada exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Token de recuperacion invalido o expirado"}), 400
    else:
        return jsonify({"mensaje": "No se encontro el token de recuperacion"}), 400



# Definición de una ruta para listar todos los usuarios por paginacion
@app.route('/users', methods=['GET'])
def list_users():
    try:
        # Realiza la conexión con la base de datos
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Obtén los parámetros de paginación de la solicitud (por defecto, página 1 y tamaño de página 10)
        page_number = int(request.args.get('page', 1))
        page_size = int(request.args.get('size', 10))

        # Calcula el índice de inicio y fin para la paginación
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size

        # Ejecuta una consulta SELECT para recuperar usuarios paginados
        cursor.execute("SELECT * FROM users LIMIT %s OFFSET %s", (page_size, start_index))
        users = cursor.fetchall()

        # Cierra el cursor y la conexión con la base de datos.
        cursor.close()
        conn.close()

        # Formatea los datos de los usuarios en formato JSON
        users_data = []
        for user in users:
            user_data = {
                "id": user[0],
                "username": user[1],
                "email": user[3]
            }
            users_data.append(user_data)

        # Crea y devuelve una respuesta JSON con la lista de usuarios paginada
        return jsonify(users_data), 200
    except Exception as e:
        # En caso de error, devuelve una respuesta JSON con el mensaje de error y el código 500 (Internal Server Error)
        return jsonify({"error": str(e)}), 500


#--------------------------------------CRUD--------------------------------------
# Definición de una ruta para el registro de usuarios
@app.route('/registro', methods=['POST'])

def registro_usuario():
    # Establecer una conexión con la base de datos PostgreSQL
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    # Obtener los datos del usuario desde la carga JSON de la solicitud HTTP
    data = request.get_json()
    username = data['username']
    password = data['password']
    email = data['email']

    # Ejecutar una consulta SQL para insertar los datos del usuario en la tabla 'users'
    cursor.execute("INSERT INTO users (username, hashed_password, email) VALUES (%s, %s, %s)",
                   (username, password, email))

    # Confirmar la transacción y cerrar el cursor y la conexión
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201


# Definición de una ruta para obtener un usuario
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        #Realiza la conexion con la base de datos
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        

        # Ejecuta una consulta SELECT para recuperar los datos del usuario según el user_id especificado       
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
    
        # Cierra el cursor y la conexión con la base de datos.
        cursor.close()
        conn.close()

        if user:
            # Extrae los datos del usuario y crea una respuesta JSON
            user_data = {
                "id": user[0],
                "username": user[1],
                "email": user[3]
            }
            return jsonify(user_data), 200
        else:
            return jsonify({"message": "El usuario no existe"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Definición de una ruta para actualizar un usuario
@app.route('/actualizacion_usuario', methods=['PUT'])
@jwt_required()
def actualizacion_usuario():
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_email = get_jwt_identity()

        # Establecer una conexión con la base de datos PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Obtener los datos de actualización desde la carga JSON de la solicitud HTTP
        data = request.get_json()
        new_email = data['new_email']

        # Actualizar el correo electrónico del usuario en la base de datos
        cursor.execute("UPDATE users SET email = %s WHERE email = %s",
                       (new_email, current_user_email))

        # Confirmar la transacción y cerrar el cursor y la conexión
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Definición de una ruta para eliminar un usuario
@app.route('/eliminacion_usuario', methods=['DELETE'])
@jwt_required()
def eliminacion_usuario():
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_email = get_jwt_identity()

        # Establecer una conexión con la base de datos PostgreSQL
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Obtener el ID del usuario desde la base de datos usando el email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (current_user_email,))
        user_id = cursor.fetchone()

        if user_id:
            # Eliminar al usuario de la base de datos
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id[0],))
            conn.commit()

            cursor.close()
            conn.close()

            return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
        else:
            return jsonify({"mensaje": "Usuario no encontrado"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#---------------------------------------FIN CRUD---------------------------------------



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)