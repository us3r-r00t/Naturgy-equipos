import logging
from functools import wraps
from pathlib import Path

import pandas as pd
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename

from db import get_db

logger = logging.getLogger(__name__)

reportes_bp = Blueprint('reportes', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            return jsonify({
                'success': False,
                'message': 'Acceso no autorizado. Inicie sesión para continuar.'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

@reportes_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No se envió ningún archivo.'}), 400

    file = request.files['file']
    raw_filename = file.filename

    if not raw_filename:
        return jsonify({'success': False, 'message': 'Nombre de archivo no válido.'}), 400

    filename = secure_filename(raw_filename)
    if not filename:
        return jsonify({'success': False, 'message': 'Nombre de archivo no válido tras sanitización.'}), 400

    ext = Path(filename).suffix.lower()

    if ext not in ['.xls', '.xlsx', '.csv']:
        return jsonify({'success': False, 'message': 'Formato no soportado. Solo .xlsx, .xls y .csv.'}), 400

    try:
        if ext in ['.xls', '.xlsx']:
            # Lee automáticamente la solapa mensual relevante si existe, o la primera por defecto
            excel_file = pd.ExcelFile(file)
            sheet_names = excel_file.sheet_names
            meses_clave = ['OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE', 'ENERO', 'LOGUEO', 'REPORTE']
            target_sheet = next(
                (s for s in sheet_names if any(m in s.upper() for m in meses_clave)),
                sheet_names[0]
            )
            df = excel_file.parse(sheet_name=target_sheet)
        else:
            try:
                df = pd.read_csv(file, encoding='utf-8')
            except UnicodeDecodeError:
                file.seek(0)
                df = pd.read_csv(file, encoding='latin-1', sep=None, engine='python')

        df = df.dropna(how='all')
        tabla_html = df.to_html(classes="tabla-logueos-estilo", index=False, border=0)

        # Guardar persistencia directa en SQLite asegurando cierre de conexión
        conn = get_db()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reportes (nombre_archivo, total_registros, html_tabla) VALUES (?, ?, ?)",
                (filename, len(df), tabla_html)
            )
            conn.commit()
        finally:
            conn.close()

        return jsonify({
            'success': True,
            'message': f"Archivo '{filename}' procesado y guardado en SQLite con éxito. Total registros: {len(df)}",
            'total': len(df),
            'html_tabla': tabla_html
        })

    except Exception as e:
        logger.exception("Error al procesar archivo %s", filename)
        return jsonify({'success': False, 'message': f"Error al procesar el archivo: {e!s}"}), 500

@reportes_bp.route('/obtener_reporte', methods=['GET'])
@login_required
def obtener_reporte():
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reportes ORDER BY id DESC LIMIT 1")
        ultimo = cursor.fetchone()
    finally:
        conn.close()

    if ultimo:
        return jsonify({
            'success': True,
            'html_tabla': ultimo['html_tabla'],
            'total': ultimo['total_registros'],
            'archivo': ultimo['nombre_archivo']
        })

    return jsonify({'success': False, 'message': 'No hay reportes cargados aún.'}), 404