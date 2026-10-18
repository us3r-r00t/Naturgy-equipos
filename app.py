import os

from flask import Flask, render_template

from db import init_db
from routes.auth import auth_bp
from routes.reportes import reportes_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'naturgy-dev-secret-key-change-in-prod')

# Configuración de seguridad para cookies de sesión
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Corregido: Limite de subida de 16 MB
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Registrar los Blueprints (módulos de rutas)
app.register_blueprint(auth_bp)
app.register_blueprint(reportes_bp)

# Inicializa la base de datos SQLite y carga user.txt al arrancar la app (compatible con WSGI)
with app.app_context():
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1')
    port = int(os.environ.get('PORT', '5000'))
    app.run(debug=debug_mode, port=port)