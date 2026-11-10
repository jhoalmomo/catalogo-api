import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import UsuarioModel, ProductoModel
from auth import generar_token, token_requerido

FRONTEND_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
app = Flask(__name__, static_folder=FRONTEND_FOLDER)

# CORS habilitado para admitir peticiones externas
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Servir frontend estático
@app.route('/', methods=['GET'])
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>', methods=['GET'])
def archivos_frontend(filename):
    return send_from_directory(app.static_folder, filename)

# POST /api/auth/login (Pública)
@app.route('/api/auth/login', methods=['POST'])
def login():
    datos = request.get_json(silent=True) or {}
    username = datos.get('username')
    password = datos.get('password')

    if not username or not password:
        return jsonify({"error": "Debe enviar 'username' y 'password'"}), 400

    usuario = UsuarioModel.validar_credenciales(username, password)
    if not usuario:
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = generar_token(usuario['id'], usuario['username'])
    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": token
    }), 200

# GET /api/productos (Pública)
@app.route('/api/productos', methods=['GET'])
def listar_productos():
    productos = ProductoModel.obtener_todos()
    return jsonify(productos), 200

# GET /api/productos/:id (Pública)
@app.route('/api/productos/<int:id>', methods=['GET'])
def detalle_producto(id):
    producto = ProductoModel.obtener_por_id(id)
    if not producto:
        return jsonify({"error": f"No se encontró el producto con ID {id}"}), 404
    return jsonify(producto), 200

# POST /api/productos (JWT)
@app.route('/api/productos', methods=['POST'])
@token_requerido
def crear_producto():
    datos = request.get_json(silent=True) or {}
    nombre = datos.get('nombre')
    precio = datos.get('precio')
    stock = datos.get('stock')

    if not nombre or precio is None or stock is None:
        return jsonify({"error": "Todos los campos (nombre, precio, stock) son requeridos"}), 400

    try:
        nuevo_id = ProductoModel.crear(str(nombre).strip(), float(precio), int(stock))
        return jsonify({"mensaje": "Producto creado con éxito", "id": nuevo_id}), 201
    except ValueError:
        return jsonify({"error": "Precio o stock con formato numérico inválido"}), 400

# PUT /api/productos/:id (JWT)
@app.route('/api/productos/<int:id>', methods=['PUT'])
@token_requerido
def actualizar_producto(id):
    if not ProductoModel.obtener_por_id(id):
        return jsonify({"error": f"El producto con ID {id} no existe"}), 404

    datos = request.get_json(silent=True) or {}
    nombre = datos.get('nombre')
    precio = datos.get('precio')
    stock = datos.get('stock')

    if not nombre or precio is None or stock is None:
        return jsonify({"error": "Todos los campos (nombre, precio, stock) son requeridos"}), 400

    try:
        ProductoModel.actualizar(id, str(nombre).strip(), float(precio), int(stock))
        return jsonify({"mensaje": f"Producto con ID {id} actualizado con éxito"}), 200
    except ValueError:
        return jsonify({"error": "Precio o stock con formato numérico inválido"}), 400

# DELETE /api/productos/:id (JWT)
@app.route('/api/productos/<int:id>', methods=['DELETE'])
@token_requerido
def eliminar_producto(id):
    if not ProductoModel.obtener_por_id(id):
        return jsonify({"error": f"El producto con ID {id} no existe"}), 404

    ProductoModel.eliminar(id)
    return jsonify({"mensaje": f"Producto con ID {id} eliminado con éxito"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
