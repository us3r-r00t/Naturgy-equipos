from flask import Blueprint, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    usuario_input = data.get('usuario', '').strip()
    password_input = data.get('password', '').strip()

    if not usuario_input or not password_input:
        return jsonify({
            'success': False,
            'message': 'Usuario o contraseña no proporcionados.'
        }), 400

    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (usuario_input,)
        )
        user = cursor.fetchone()

        if user:
            # Soporta verificación por hash y migración transparente de passwords legacy en texto plano
            is_valid = False
            if user['password'].startswith(('scrypt:', 'pbkdf2:')):
                is_valid = check_password_hash(user['password'], password_input)
            elif user['password'] == password_input:
                is_valid = True
                cursor.execute(
                    "UPDATE usuarios SET password = ? WHERE id = ?",
                    (generate_password_hash(password_input), user['id'])
                )
                conn.commit()

            if is_valid:
                session['usuario'] = user['username']
                session['rol'] = user['rol']
                return jsonify({
                    'success': True,
                    'usuario': user['username'],
                    'rol': user['rol']
                })
    finally:
        conn.close()

    return jsonify({
        'success': False,
        'message': 'Usuario o contraseña incorrectos.'
    }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})