import jwt

token = "generado"
jwt_secret_key = "ls"

try:
    decoded_payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
    print(decoded_payload)
except jwt.ExpiredSignatureError:
    print("Token expirado")
except jwt.InvalidTokenError:
    print("Token inválido")
