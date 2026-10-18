import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest

# Usar base de datos temporal para pruebas
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
os.close(temp_db_fd)
os.environ['DATABASE_NAME'] = temp_db_path
os.environ['SECRET_KEY'] = 'test-secret-key-12345'

from werkzeug.security import generate_password_hash

from app import app
from db import get_db, init_db


@pytest.fixture(scope='session', autouse=True)
def setup_test_db():
    with app.app_context():
        init_db()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'testuser'")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO usuarios (username, password, rol, equipo) VALUES (?, ?, ?, ?)",
                ('testuser', generate_password_hash('Password123*'), 'lider', 'TEST')
            )
            conn.commit()
        conn.close()
    yield
    if os.path.exists(temp_db_path):
        os.remove(temp_db_path)

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_login_success(client):
    res = client.post('/login', json={'usuario': 'testuser', 'password': 'Password123*'})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['usuario'] == 'testuser'
    assert data['rol'] == 'lider'

def test_login_invalid_password(client):
    res = client.post('/login', json={'usuario': 'testuser', 'password': 'wrongpassword'})
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False

def test_unauthenticated_access_blocked(client):
    # Sin sesión iniciada, /upload y /obtener_reporte deben retornar 401
    res_upload = client.post('/upload')
    assert res_upload.status_code == 401
    assert res_upload.get_json()['success'] is False

    res_reporte = client.get('/obtener_reporte')
    assert res_reporte.status_code == 401
    assert res_reporte.get_json()['success'] is False

def test_authenticated_upload_and_retrieval(client):
    # Iniciar sesión
    login_res = client.post('/login', json={'usuario': 'testuser', 'password': 'Password123*'})
    assert login_res.status_code == 200

    # Subir un archivo CSV de prueba
    csv_content = b"AGENTE,HORA_INGRESO,HORA_SALIDA\nJuan Perez,09:00,18:00\nMaria Lopez,10:00,19:00\n"
    data = {
        'file': (io.BytesIO(csv_content), 'reporte_turnos.csv')
    }
    upload_res = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 200
    upload_data = upload_res.get_json()
    assert upload_data['success'] is True
    assert upload_data['total'] == 2

    # Consultar reporte guardado
    get_res = client.get('/obtener_reporte')
    assert get_res.status_code == 200
    get_data = get_res.get_json()
    assert get_data['success'] is True
    assert get_data['total'] == 2
    assert get_data['archivo'] == 'reporte_turnos.csv'

def test_cookie_security_flags(client):
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
