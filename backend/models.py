import os
import json
from datetime import datetime

# Ruta absoluta al archivo JSON dentro de la carpeta backend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "productos.json")


def _cargar_productos():
    """Lee y retorna la lista de productos desde el archivo productos.json."""
    if not os.path.exists(DATA_FILE):
        # Datos iniciales si el archivo no existe
        datos_iniciales = [
            {"id": 1, "nombre": "Portátil ASUS TUF", "precio": 4200000.0, "stock": 6, "fecha_creacion": "2026-11-10 10:00:00"},
            {"id": 2, "nombre": "Teclado Mecánico RGB", "precio": 250000.0, "stock": 12, "fecha_creacion": "2026-11-10 10:05:00"},
            {"id": 3, "nombre": "Mouse Ergonómico", "precio": 85000.0, "stock": 20, "fecha_creacion": "2026-11-10 10:10:00"}
        ]
        _guardar_productos(datos_iniciales)
        return datos_iniciales

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _guardar_productos(productos):
    """Escribe la lista actualizada de productos en el archivo productos.json."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(productos, f, indent=4, ensure_ascii=False)


class UsuarioModel:
    """Modelo simple para validar credenciales de autenticación."""
    
    USUARIOS_VALIDOS = [
        {"id": 1, "username": "admin", "password": "admin123"}
    ]

    @staticmethod
    def validar_credenciales(username, password):
        """Busca el usuario en la lista predefinida."""
        for u in UsuarioModel.USUARIOS_VALIDOS:
            if u["username"] == username and u["password"] == password:
                return {"id": u["id"], "username": u["username"]}
        return None


class ProductoModel:
    """Modelo responsable de las operaciones CRUD leyendo y escribiendo en el archivo JSON."""

    @staticmethod
    def obtener_todos():
        """Retorna todos los productos ordenados del más reciente al más antiguo."""
        productos = _cargar_productos()
        return sorted(productos, key=lambda x: x["id"], reverse=True)

    @staticmethod
    def obtener_por_id(id_producto):
        """Busca un producto por su ID."""
        productos = _cargar_productos()
        for p in productos:
            if p["id"] == id_producto:
                return p
        return None

    @staticmethod
    def crear(nombre, precio, stock):
        """Inserta un nuevo producto asignándole un ID autoincremental."""
        productos = _cargar_productos()
        nuevo_id = max([p["id"] for p in productos], default=0) + 1
        
        nuevo_producto = {
            "id": nuevo_id,
            "nombre": nombre,
            "precio": float(precio),
            "stock": int(stock),
            "fecha_creacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        productos.append(nuevo_producto)
        _guardar_productos(productos)
        return nuevo_id

    @staticmethod
    def actualizar(id_producto, nombre, precio, stock):
        """Modifica un producto existente."""
        productos = _cargar_productos()
        encontrado = False
        for p in productos:
            if p["id"] == id_producto:
                p["nombre"] = nombre
                p["precio"] = float(precio)
                p["stock"] = int(stock)
                encontrado = True
                break

        if encontrado:
            _guardar_productos(productos)
        return encontrado

    @staticmethod
    def eliminar(id_producto):
        """Elimina un producto por su ID."""
        productos = _cargar_productos()
        longitud_inicial = len(productos)
        productos_filtrados = [p for p in productos if p["id"] != id_producto]

        if len(productos_filtrados) < longitud_inicial:
            _guardar_productos(productos_filtrados)
            return True
        return False
