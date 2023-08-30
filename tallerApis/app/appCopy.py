from flask import Flask, request, jsonify
import psycopg2
import bcrypt
import jwt
import datetime

app = Flask(__name__)
# Configuración de la base de datos
db_config = {
    'dbname': 'authentication_db',
    'user': 'admin',
    'password': 'admin_password',
    'host': 'auth_postgres'
}

jwt_secret_key = "clavesecreta"

@app.route('/login', methods=['POST'])
def login():
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        data = request.get_json()
        username = data['username']
        password = data['password']

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            # Generar un token JWT
            payload = {
                'user_id': user[0],
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # El token expira en 1 hora
            }
            token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')

            return jsonify({"token": token.decode('utf-8')}), 200
        else:
            return jsonify({"message": "Credenciales inválidas"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Definición de una ruta para el registro de usuarios
@app.route('/register', methods=['POST'])
def register_user():
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

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user:
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

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        data = request.get_json()
        new_username = data['username']
        new_email = data['email']

        cursor.execute("UPDATE users SET username = %s, email = %s WHERE user_id = %s",
                       (new_username, new_email, user_id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)





    @app.route('/login', methods=['POST'])
def login():
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor()

    data = request.get_json()
    email = data['email']
    password = data['password']

    # Verificar las credenciales del usuario en la base de datos
    cursor.execute("SELECT email, hashed_password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user[1] == password:
        user_id = user[0]
        # Generar un token
        token = jwt.encode({'username': username}, secret_key, algorithm='HS256')
        conn.close()
        return jsonify({"token": token}), 200
    else:
        conn.close()
        return jsonify({"error": "Credenciales invalidas"}), 401
