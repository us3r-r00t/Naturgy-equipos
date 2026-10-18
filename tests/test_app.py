import io
import os
import sys
import tempfile

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import pytest
from werkzeug.security import generate_password_hash

# Usar base de datos temporal para pruebas
temp_db_fd, temp_db_path = tempfile.mkstemp(suffix='.db')
os.close(temp_db_fd)
os.environ['DATABASE_NAME'] = temp_db_path
os.environ['SECRET_KEY'] = 'test-secret-key-12345'

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
            cursor.execute(
                "INSERT INTO usuarios (username, password, rol, equipo) VALUES (?, ?, ?, ?)",
                ('legacyuser', 'PlainTextPassword2026', 'agente', 'BAN CAU')
            )
            conn.commit()
        conn.close()
    yield
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except OSError:
            pass

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

def test_login_empty_payload(client):
    res = client.post('/login', json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False

def test_legacy_plaintext_password_auto_migration(client):
    # Probar que un usuario con clave legacy en texto plano puede loguearse
    res = client.post('/login', json={'usuario': 'legacyuser', 'password': 'PlainTextPassword2026'})
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Verificar que en base de datos la clave se convirtió a un hash seguro
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM usuarios WHERE username = 'legacyuser'")
    migrated_pw = cursor.fetchone()[0]
    conn.close()
    assert migrated_pw.startswith(('scrypt:', 'pbkdf2:'))

def test_unauthenticated_access_blocked(client):
    # Sin sesión iniciada, /upload y /obtener_reporte deben retornar 401
    res_upload = client.post('/upload')
    assert res_upload.status_code == 401
    assert res_upload.get_json()['success'] is False

    res_reporte = client.get('/obtener_reporte')
    assert res_reporte.status_code == 401
    assert res_reporte.get_json()['success'] is False

def test_authenticated_upload_and_retrieval_csv(client):
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

def test_authenticated_upload_excel_with_dynamic_sheet(client):
    # Loguear
    client.post('/login', json={'usuario': 'testuser', 'password': 'Password123*'})

    # Generar Excel con solapa 'NOVIEMBRE' (distinta a la hardcodeada 'OCTUBRE')
    buf = io.BytesIO()
    df_excel = pd.DataFrame({
        'AGENTE': ['Carlos Gomez', 'Laura Diaz'],
        'EQUIPO': ['NOA CAU', 'NOA CAU']
    })
    with pd.ExcelWriter(buf, engine='openpyxl') as writer:
        df_excel.to_excel(writer, sheet_name='NOVIEMBRE', index=False)
    buf.seek(0)

    data = {
        'file': (buf, 'orion_noviembre.xlsx')
    }
    upload_res = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 200
    data_res = upload_res.get_json()
    assert data_res['success'] is True
    assert data_res['total'] == 2

def test_upload_path_traversal_sanitization(client):
    client.post('/login', json={'usuario': 'testuser', 'password': 'Password123*'})

    # Intentar subir con ruta de path traversal
    csv_content = b"COL1,COL2\nval1,val2\n"
    data = {
        'file': (io.BytesIO(csv_content), '../../../../malicious_file.csv')
    }
    upload_res = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 200
    upload_data = upload_res.get_json()
    assert upload_data['success'] is True

    # Comprobar que en DB el archivo fue guardado con nombre sanitizado sin '../'
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre_archivo FROM reportes ORDER BY id DESC LIMIT 1")
    nombre_guardado = cursor.fetchone()[0]
    conn.close()
    assert nombre_guardado == 'malicious_file.csv'
    assert '..' not in nombre_guardado

def test_upload_invalid_extension_rejected(client):
    client.post('/login', json={'usuario': 'testuser', 'password': 'Password123*'})

    data = {
        'file': (io.BytesIO(b"malicious script"), 'exploit.sh')
    }
    upload_res = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload_res.status_code == 400
    assert upload_res.get_json()['success'] is False

def test_cookie_security_flags(client):
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
