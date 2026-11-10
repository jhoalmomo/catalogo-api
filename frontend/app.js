const API_URL = '/api';
let modalProductoInstance = null;
let modalLoginInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    modalProductoInstance = new bootstrap.Modal(document.getElementById('modalProducto'));
    modalLoginInstance = new bootstrap.Modal(document.getElementById('modalLogin'));

    actualizarEstadoAuth();
    cargarProductos();

    // Eventos
    document.getElementById('btn-submit-login').addEventListener('click', iniciarSesion);
    document.getElementById('btn-logout').addEventListener('click', cerrarSesion);
    document.getElementById('btn-guardar-producto').addEventListener('click', guardarProducto);
    document.getElementById('btn-nuevo-producto').addEventListener('click', prepararCreacion);
});

function obtenerToken() {
    return localStorage.getItem('jwt_token');
}

function actualizarEstadoAuth() {
    const token = obtenerToken();
    const btnAbrirLogin = document.getElementById('btn-abrir-login');
    const panelSesion = document.getElementById('panel-sesion');
    const btnNuevo = document.getElementById('btn-nuevo-producto');
    const alerta = document.getElementById('alerta-publica');

    if (token) {
        btnAbrirLogin.classList.add('d-none');
        panelSesion.classList.remove('d-none');
        panelSesion.classList.add('d-flex');
        btnNuevo.classList.remove('d-none');
        alerta.classList.add('d-none');
    } else {
        btnAbrirLogin.classList.remove('d-none');
        panelSesion.classList.add('d-none');
        panelSesion.classList.remove('d-flex');
        btnNuevo.classList.add('d-none');
        alerta.classList.remove('d-none');
    }
}

async function iniciarSesion() {
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value.trim();

    try {
        const respuesta = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const datos = await respuesta.json();

        if (respuesta.ok) {
            localStorage.setItem('jwt_token', datos.token);
            modalLoginInstance.hide();
            actualizarEstadoAuth();
            cargarProductos();
        } else {
            alert(datos.error || 'Error al iniciar sesión');
        }
    } catch (err) {
        alert('No se pudo conectar con el servidor.');
    }
}

function cerrarSesion() {
    localStorage.removeItem('jwt_token');
    actualizarEstadoAuth();
    cargarProductos();
}

async function cargarProductos() {
    try {
        const respuesta = await fetch(`${API_URL}/productos`);
        const productos = await respuesta.json();

        const tbody = document.getElementById('tabla-cuerpo');
        tbody.innerHTML = '';

        const token = obtenerToken();

        productos.forEach(p => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${p.id}</td>
                <td>${p.nombre}</td>
                <td>$ ${Number(p.precio).toLocaleString('es-CO')}</td>
                <td>${p.stock}</td>
                <td>
                    ${token ? `
                        <button class="btn btn-warning btn-sm me-1" onclick="prepararEdicion(${p.id}, '${p.nombre}', ${p.precio}, ${p.stock})">Editar</button>
                        <button class="btn btn-danger btn-sm" onclick="eliminarProducto(${p.id})">Eliminar</button>
                    ` : '<span class="text-secondary small">Solo lectura</span>'}
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error('Error al cargar productos:', err);
    }
}

function prepararCreacion() {
    document.getElementById('modal-producto-titulo').textContent = 'Nuevo Producto';
    document.getElementById('prod-id').value = '';
    document.getElementById('prod-nombre').value = '';
    document.getElementById('prod-precio').value = '';
    document.getElementById('prod-stock').value = '';
}

function prepararEdicion(id, nombre, precio, stock) {
    document.getElementById('modal-producto-titulo').textContent = `Editar Producto #${id}`;
    document.getElementById('prod-id').value = id;
    document.getElementById('prod-nombre').value = nombre;
    document.getElementById('prod-precio').value = precio;
    document.getElementById('prod-stock').value = stock;
    modalProductoInstance.show();
}

async function guardarProducto() {
    const id = document.getElementById('prod-id').value;
    const nombre = document.getElementById('prod-nombre').value.trim();
    const precio = parseFloat(document.getElementById('prod-precio').value);
    const stock = parseInt(document.getElementById('prod-stock').value);

    if (!nombre || isNaN(precio) || isNaN(stock)) {
        alert('Por favor complete todos los campos con valores válidos.');
        return;
    }

    const token = obtenerToken();
    const metodo = id ? 'PUT' : 'POST';
    const url = id ? `${API_URL}/productos/${id}` : `${API_URL}/productos`;

    try {
        const respuesta = await fetch(url, {
            method: metodo,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ nombre, precio, stock })
        });

        const resultado = await respuesta.json();
        if (respuesta.ok) {
            modalProductoInstance.hide();
            cargarProductos();
        } else {
            alert(resultado.error || 'Error en la operación');
        }
    } catch (err) {
        alert('Error de conexión con el backend.');
    }
}

async function eliminarProducto(id) {
    if (!confirm(`¿Seguro que deseas eliminar el producto #${id}?`)) return;

    const token = obtenerToken();
    try {
        const respuesta = await fetch(`${API_URL}/productos/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (respuesta.ok) {
            cargarProductos();
        } else {
            const resultado = await respuesta.json();
            alert(resultado.error || 'Error al eliminar');
        }
    } catch (err) {
        alert('Error al conectar con el servidor.');
    }
}
