import os
import re
import pandas as pd
from flask import Flask, request, jsonify, render_template, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_naturgy_2026'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Base de datos de usuarios (USERS.txt)
USUARIOS = {
    "kparra": {"password": "admin2026", "rol": "lider", "equipo": "TODOS"},
    "lherrera": {"password": "admin2026", "rol": "lider", "equipo": "TODOS"},
    "operador_bancau": {"password": "BanCau2026*", "rol": "operador", "equipo": "NATURGY BAN CAU"},
    "operador_noacau": {"password": "NoaCau2026*", "rol": "operador", "equipo": "NATURGY NOA CAU"},
    "operador_sanjuan": {"password": "SanJuan2026*", "rol": "operador", "equipo": "NATURGY ENERGIA SAN JUAN"}
}

def clean_str(val):
    if pd.isna(val) or val is None:
        return ''
    return str(val).strip()

def procesar_archivo_reporte(filepath):
    # CORREGIDO: Garantizar obtención de la extensión como cadena de texto
    split_res = os.path.splitext(filepath)
    ext = str(split_res[1]).lower() if isinstance(split_res, (list, tuple)) else str(split_res).lower()
    df_raw = None
    
    # 1. Intentar lectura como Excel
    if ext in ['.xlsx', '.xls']:
        for engine in ['openpyxl', 'xlrd', None]:
            try:
                df_raw = pd.read_excel(filepath, sheet_name=0, header=None, engine=engine)
                if df_raw is not None and not df_raw.empty:
                    break
            except Exception:
                pass

    # 2. Intentar lectura como CSV
    if df_raw is None or df_raw.empty:
        for enc in ['utf-8', 'latin1', 'cp1252']:
            for sep in [';', ',', '\t', None]:
                try:
                    df_raw = pd.read_csv(filepath, sep=sep, encoding=enc, header=None, on_bad_lines='skip', engine='python')
                    if df_raw is not None and not df_raw.empty and df_raw.shape[1] > 1:
                        break
                except Exception:
                    pass
            if df_raw is not None and not df_raw.empty and df_raw.shape[1] > 1:
                break

    if df_raw is None or df_raw.empty:
        return []

    raw_text_list = [clean_str(x) for x in df_raw.values.flatten()]
    raw_text = ' '.join([x for x in raw_text_list if x])

    # CASO A: Reporte Individual del sistema (reporte_csv.csv)
    if 'AGENTE:' in raw_text.upper() or 'REPORTE MENSUAL POR AGENTE' in raw_text.upper():
        agente = 'ASESOR'
        for r_idx in range(min(10, len(df_raw))):
            row_vals = [clean_str(x) for x in df_raw.iloc[r_idx].values]
            row_str = ' '.join([x for x in row_vals if x])
            if 'AGENTE:' in row_str.upper():
                m = re.search(r'AGENTE:\s*([^;|\n\r]+)', row_str, re.IGNORECASE)
                if m:
                    agente = m.group(1).strip()
                    break

        header_idx = None
        for r_idx in range(min(15, len(df_raw))):
            row_vals = [clean_str(x) for x in df_raw.iloc[r_idx].values]
            row_str = ' '.join([x for x in row_vals if x]).upper()
            if 'DESCRIPCION' in row_str or 'DESCRIPCIÓN' in row_str:
                header_idx = r_idx
                break

        if header_idx is not None:
            header_row = [clean_str(x) for x in df_raw.iloc[header_idx].values]
            df_data = df_raw.iloc[header_idx + 1:].copy()
            df_data.columns = header_row
        else:
            df_data = df_raw.copy()

        desc_col = None
        for col in df_data.columns:
            if 'DESCRIP' in str(col).upper():
                desc_col = col
                break

        if desc_col is None:
            return []

        df_in = df_data[df_data[desc_col].astype(str).str.strip().str.upper() == 'HORA DE ENTRADA']
        df_out = df_data[df_data[desc_col].astype(str).str.strip().str.upper() == 'HORA DE SALIDA']

        if df_in.empty or df_out.empty:
            return []

        ignore_keywords = ['GRUPO', 'DESCRIP', 'TOTAL', 'UNNAMED', 'NAN', 'NONE']
        date_cols = []
        for col in df_data.columns:
            c_str = str(col).strip()
            c_upper = c_str.upper()
            if c_str != '' and not any(k in c_upper for k in ignore_keywords):
                date_cols.append(col)

        row1 = {'Asesor': agente, 'DESCRIPCION': 'Hora de Entrada'}
        row2 = {'Asesor': '', 'DESCRIPCION': 'Hora de Salida'}

        for col in date_cols:
            col_name = str(col).strip()
            v_in_vals = df_in[col].values
            v_out_vals = df_out[col].values
            
            v_in = v_in_vals[0] if len(v_in_vals) > 0 else '---'
            v_out = v_out_vals[0] if len(v_out_vals) > 0 else '---'
            
            str_in = clean_str(v_in)
            str_out = clean_str(v_out)
            
            row1[col_name] = str_in if str_in and str_in.lower() != 'nan' else '---'
            row2[col_name] = str_out if str_out and str_out.lower() != 'nan' else '---'

        return [pd.DataFrame([row1, row2])]

    # CASO B: Archivo grupal
    blocks = []
    current_agent = None
    dates = []

    for r_idx in range(len(df_raw)):
        row_vals = [clean_str(x) for x in df_raw.iloc[r_idx].values]
        row_str = ' '.join([x for x in row_vals if x]).upper()
        
        v0 = row_vals[0] if len(row_vals) > 0 else ''
        v1 = row_vals[1] if len(row_vals) > 1 else ''

        if v1.upper() in ['DESCRIPCION', 'DESCRIPCIÓN']:
            current_agent = v0 if v0 else 'ASESOR'
            if r_idx + 1 < len(df_raw):
                next_vals = [clean_str(x) for x in df_raw.iloc[r_idx + 1].values]
                dates = [v for v in next_vals if v and any(t in v.lower() for t in ['oct', 'sep', '/', '-'])]
            continue

        if 'HORA DE ENTRADA' in row_str:
            in_vals = [v for v in row_vals if v]
            out_vals = []
            if r_idx + 1 < len(df_raw):
                out_vals = [clean_str(x) for x in df_raw.iloc[r_idx + 1].values if clean_str(x)]

            row1 = {'Asesor': current_agent or 'ASESOR', 'DESCRIPCION': 'Hora de Entrada'}
            row2 = {'Asesor': '', 'DESCRIPCION': 'Hora de Salida'}

            in_times = [v for v in in_vals if v not in [current_agent, 'DESCRIPCION', 'Hora de Entrada'] and v.lower() != 'nan']
            out_times = [v for v in out_vals if v not in ['DESCRIPCION', 'Hora de Salida'] and v.lower() != 'nan']

            for d_idx, d_name in enumerate(dates):
                v_in = in_times[d_idx] if d_idx < len(in_times) else '---'
                v_out = out_times[d_idx] if d_idx < len(out_times) else '---'
                row1[d_name] = v_in if v_in and v_in.lower() != 'nan' else '---'
                row2[d_name] = v_out if v_out and v_out.lower() != 'nan' else '---'

            blocks.append(pd.DataFrame([row1, row2]))

    return blocks

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    usuario = data.get('usuario', '').strip()
    password = data.get('password', '').strip()
    equipo_solicitado = data.get('equipo', '').strip()

    if usuario not in USUARIOS or USUARIOS[usuario]['password'] != password:
        return jsonify({"success": False, "message": "Usuario o contraseña incorrectos"}), 401

    user_info = USUARIOS[usuario]

    if user_info['rol'] != 'lider' and user_info['equipo'] != equipo_solicitado:
        return jsonify({
            "success": False, 
            "message": f"Acceso denegado: El usuario '{usuario}' solo puede ingresar al equipo '{user_info['equipo']}'."
        }), 403

    session['usuario'] = usuario
    session['rol'] = user_info['rol']
    session['equipo'] = equipo_solicitado if user_info['rol'] == 'lider' else user_info['equipo']

    return jsonify({
        "success": True,
        "usuario": usuario,
        "rol": user_info['rol'],
        "equipo": session['equipo']
    })

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/upload', methods=['POST'])
def upload_file():
    if session.get('rol') != 'lider':
        return jsonify({"success": False, "message": "Se requieren permisos de Líder."}), 403

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se adjuntó ningún archivo."}), 400

    file = request.files['file']
    if file.filename == '' or file.filename == '[object FileList]':
        return jsonify({"success": False, "message": "Por favor selecciona un archivo válido."}), 400

    filename = secure_filename(file.filename)
    split_res = os.path.splitext(filename)
    ext = str(split_res[1]).lower() if isinstance(split_res, (list, tuple)) else str(split_res).lower()
    
    if ext not in ['.csv', '.xlsx', '.xls']:
        return jsonify({"success": False, "message": "Formato de archivo no permitido. Debe ser .csv, .xlsx o .xls."}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    return jsonify({
        "success": True,
        "message": f"Reporte '{filename}' cargado correctamente."
    })

@app.route('/obtener_reporte', methods=['GET'])
def obtener_reporte():
    if 'usuario' not in session:
        return jsonify({"success": False, "message": "Sesión no iniciada"}), 401

    equipo_activo = session.get('equipo')

    archivos = [
        os.path.join(app.config['UPLOAD_FOLDER'], f) 
        for f in os.listdir(app.config['UPLOAD_FOLDER']) 
        if f.endswith(('.csv', '.xlsx', '.xls'))
    ]

    if not archivos:
        return jsonify({
            "success": False, 
            "message": "No hay reportes cargados aún para este equipo."
        })

    try:
        all_blocks = []
        for archivo in archivos:
            blocks = procesar_archivo_reporte(archivo)
            all_blocks.extend(blocks)

        if not all_blocks:
            return jsonify({"success": False, "message": "No se pudieron procesar los datos de las planillas."})

        seen_advisors = set()
        dedup_blocks = []
        for block in reversed(all_blocks):
            adv_name = clean_str(block['Asesor'].iloc[0]) if len(block) > 0 and 'Asesor' in block.columns else ''
            if adv_name and adv_name != 'ASESOR':
                if adv_name not in seen_advisors:
                    seen_advisors.add(adv_name)
                    dedup_blocks.append(block)
            else:
                dedup_blocks.append(block)

        dedup_blocks.reverse()
        df_consolidado = pd.concat(dedup_blocks, ignore_index=True).fillna('---')

        html_tabla = df_consolidado.to_html(
            classes='table table-striped tabla-reporte', 
            index=False
        )

        return jsonify({
            "success": True,
            "equipo": equipo_activo,
            "html_tabla": html_tabla
        })

    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Error al procesar la consolidación: {str(e)}"
        }), 500

def procesar_excel_calidad_detalle(filepath):
    split_res = os.path.splitext(filepath)
    ext = str(split_res[1]).lower() if isinstance(split_res, (list, tuple)) else str(split_res).lower()
    df_raw = None
    
    if ext in ['.xlsx', '.xls']:
        for engine in ['openpyxl', 'xlrd', None]:
            try:
                df_raw = pd.read_excel(filepath, sheet_name=0, header=None, engine=engine)
                if df_raw is not None and not df_raw.empty:
                    break
            except Exception:
                pass
                
    if df_raw is None or df_raw.empty:
        for enc in ['utf-8', 'latin1', 'cp1252']:
            try:
                df_raw = pd.read_csv(filepath, sep=None, encoding=enc, header=None, engine='python')
                if df_raw is not None and not df_raw.empty:
                    break
            except Exception:
                pass

    if df_raw is None or df_raw.empty:
        return None

    header_idx = None
    for r_idx in range(min(20, len(df_raw))):
        row_str = ' '.join([clean_str(x) for x in df_raw.iloc[r_idx].values]).upper()
        if 'LEGAJO' in row_str and 'ASESOR' in row_str:
            header_idx = r_idx
            break

    if header_idx is None:
        return None

    header_cols = [clean_str(x) for x in df_raw.iloc[header_idx].values]
    df_data = df_raw.iloc[header_idx + 1:].copy()
    df_data.columns = header_cols

    df_data = df_data.dropna(how='all')
    if df_data.empty:
        return None

    def formato_nota(val):
        try:
            num = float(str(val).replace('%', '').replace(',', '.').strip())
            if num >= 85:
                return f'<span class="badge-cumple">{num:.1f}%</span>'
            else:
                return f'<span class="badge-nocumple">{num:.1f}%</span>'
        except Exception:
            return clean_str(val)

    if 'NOTA ENC' in df_data.columns:
        df_data['NOTA ENC'] = df_data['NOTA ENC'].apply(formato_nota)

    return df_data.fillna('---')

@app.route('/upload_calidad_resumen', methods=['POST'])
def upload_calidad_resumen():
    if session.get('rol') and session.get('rol') != 'lider':
        return jsonify({"success": False, "message": "Se requieren permisos de Líder."}), 403

    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No se adjuntó ningún archivo."}), 400

    file = request.files['file']
    if file.filename == '' or file.filename == '[object FileList]':
        return jsonify({"success": False, "message": "Archivo no seleccionado o no válido."}), 400

    try:
        upload_dir = app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_dir, 'resumen_' + filename)
        file.save(filepath)

        split_res = os.path.splitext(filepath)
        ext = str(split_res[1]).lower() if isinstance(split_res, (list, tuple)) else str(split_res).lower()
        df_raw = None

        # 1. Leer la solapa 'Consolidados por RAC'
        if ext in ['.xlsx', '.xls', '.xlsm']:
            try:
                xl = pd.ExcelFile(filepath)
                target_sheet = None
                for sheet in xl.sheet_names:
                    if 'CONSOLIDADOS POR RAC' in sheet.upper() or 'CONSOLIDADO' in sheet.upper():
                        target_sheet = sheet
                        break

                if target_sheet is None and xl.sheet_names:
                    target_sheet = xl.sheet_names[0]

                if target_sheet:
                    for engine in ['openpyxl', 'xlrd', None]:
                        try:
                            df_raw = pd.read_excel(filepath, sheet_name=target_sheet, header=None, engine=engine)
                            if df_raw is not None and not df_raw.empty:
                                break
                        except Exception:
                            continue
            except Exception as e_xl:
                print("Aviso al abrir libro Excel:", str(e_xl))

        if df_raw is None or df_raw.empty:
            for enc in ['utf-8', 'latin1', 'cp1252']:
                for sep in [';', ',', '\t', None]:
                    try:
                        df_raw = pd.read_csv(filepath, sep=sep, encoding=enc, header=None, on_bad_lines='skip', engine='python')
                        if df_raw is not None and not df_raw.empty and df_raw.shape[1] > 1:
                            break
                    except Exception:
                        continue
                if df_raw is not None and not df_raw.empty:
                    break

        if df_raw is None or df_raw.empty:
            return jsonify({"success": False, "message": "No se encontraron datos en la hoja 'Consolidados por RAC'."}), 400

        # 2. Localizar la fila de encabezados de la Tabla Principal
        header_idx = None
        for r_idx in range(len(df_raw)):
            row_str = ' '.join([clean_str(x).upper() for x in df_raw.iloc[r_idx].values if pd.notna(x)])
            if 'LEGAJO' in row_str and 'ASESOR' in row_str and ('LÍDER' in row_str or 'LIDER' in row_str):
                header_idx = r_idx
                break

        if header_idx is None:
            return jsonify({"success": False, "message": "No se encontró la tabla principal en la planilla."}), 400

        raw_headers = [clean_str(x).upper() for x in df_raw.iloc[header_idx].values]
        
        # Mapear índices numéricos excluyendo Estado y 4º Monitoreo
        idx_map = {}
        for c_idx, h_text in enumerate(raw_headers):
            if ('LÍDER' in h_text or 'LIDER' in h_text) and 'Líder' not in idx_map:
                idx_map['Líder'] = c_idx
            elif 'ASESOR' in h_text and 'Asesor' not in idx_map:
                idx_map['Asesor'] = c_idx
            elif '1' in h_text and 'MONITOREO' in h_text and '1º Monitoreo' not in idx_map:
                idx_map['1º Monitoreo'] = c_idx
            elif '2' in h_text and 'MONITOREO' in h_text and '2º Monitoreo' not in idx_map:
                idx_map['2º Monitoreo'] = c_idx
            elif '3' in h_text and 'MONITOREO' in h_text and '3º Monitoreo' not in idx_map:
                idx_map['3º Monitoreo'] = c_idx
            elif 'QM' in h_text and 'QM' not in idx_map:
                idx_map['QM'] = c_idx
            elif ('NOTA' in h_text or 'FINAL' in h_text) and 'Nota Final' not in idx_map:
                idx_map['Nota Final'] = c_idx

        # 3. Funciones auxiliares de formateo
        def formatear_nota(num):
            try:
                val_num = float(num)
                if val_num >= 85.0:
                    return f'<span class="badge-cumple">{val_num:.2f}%</span>'
                else:
                    return f'<span class="badge-nocumple">{val_num:.2f}%</span>'
            except Exception:
                return '---'

        def parse_float(val):
            v_str = clean_str(val)
            if not v_str or v_str.upper() in ['', 'NAN', 'NONE', '---', '#¡DIV/0!']:
                return None
            try:
                num = float(v_str.replace('%', '').replace(',', '.').strip())
                if 0 < num <= 1.0:
                    num = num * 100
                return num
            except Exception:
                return None

        def parse_int(val):
            v_str = clean_str(val)
            if not v_str or v_str.upper() in ['', 'NAN', 'NONE', '---', '#¡DIV/0!']:
                return 0
            try:
                return int(float(v_str.replace(',', '.').strip()))
            except Exception:
                return 0

        # 4. Procesar la tabla de asesores
        rows_asesores = []
        lideres_definidos = [
            'HERRERA FERNANDEZ, LEILA SABRINA',
            'PARRA YAÑEZ, KARINA BEATRIZ'
        ]

        matrix_data = df_raw.iloc[header_idx + 1:].values

        for row in matrix_data:
            lider_val = clean_str(row[idx_map['Líder']]) if 'Líder' in idx_map and idx_map['Líder'] < len(row) else ''
            asesor_val = clean_str(row[idx_map['Asesor']]) if 'Asesor' in idx_map and idx_map['Asesor'] < len(row) else ''

            if asesor_val.upper() in ['', 'ASESOR', 'NAN', 'NONE', 'NONETYPE']:
                continue

            lider_coincide = None
            for l_target in lideres_definidos:
                if l_target.upper() in lider_val.upper():
                    lider_coincide = l_target
                    break

            if lider_coincide:
                m1_num = parse_float(row[idx_map['1º Monitoreo']]) if '1º Monitoreo' in idx_map else None
                m2_num = parse_float(row[idx_map['2º Monitoreo']]) if '2º Monitoreo' in idx_map else None
                m3_num = parse_float(row[idx_map['3º Monitoreo']]) if '3º Monitoreo' in idx_map else None
                qm_num = parse_int(row[idx_map['QM']]) if 'QM' in idx_map else 0
                nota_num = parse_float(row[idx_map['Nota Final']]) if 'Nota Final' in idx_map else None

                rows_asesores.append({
                    'Líder': lider_coincide,
                    'Asesor': asesor_val,
                    '1º Monitoreo': formatear_nota(m1_num) if m1_num is not None else '---',
                    '2º Monitoreo': formatear_nota(m2_num) if m2_num is not None else '---',
                    '3º Monitoreo': formatear_nota(m3_num) if m3_num is not None else '---',
                    'QM': str(qm_num),
                    'Nota Final': formatear_nota(nota_num) if nota_num is not None else '---',
                    '_qm_raw': qm_num,
                    '_nota_raw': nota_num
                })

        # 5. Calcular dinámicamente la Tabla Resumen (Team Leader, Monitoreos Totales y Promedios)
        rows_tl = []
        total_campana_qm = 0
        notas_campana = []

        for l_target in lideres_definidos:
            asesores_lider = [r for r in rows_asesores if r['Líder'] == l_target]
            sum_qm = sum(r['_qm_raw'] for r in asesores_lider)
            notas_validas = [r['_nota_raw'] for r in asesores_lider if r['_nota_raw'] is not None]
            prom_nota = (sum(notas_validas) / len(notas_validas)) if notas_validas else None

            total_campana_qm += sum_qm
            notas_campana.extend(notas_validas)

            rows_tl.append({
                'Team Leader': l_target,
                'Monitoreos': str(sum_qm),
                'TOTAL': formatear_nota(prom_nota) if prom_nota is not None else '---'
            })

        # Agregar Fila Total Campaña
        prom_campana = (sum(notas_campana) / len(notas_campana)) if notas_campana else None
        rows_tl.append({
            'Team Leader': 'TOTAL CAMPAÑA',
            'Monitoreos': str(total_campana_qm),
            'TOTAL': formatear_nota(prom_campana) if prom_campana is not None else '---'
        })

        # Limpiar llaves temporales del listado de asesores
        for r in rows_asesores:
            r.pop('_qm_raw', None)
            r.pop('_nota_raw', None)

        # 6. Generar DataFrames y vistas HTML
        cols_finales_asesor = ['Líder', 'Asesor', '1º Monitoreo', '2º Monitoreo', '3º Monitoreo', 'QM', 'Nota Final']
        df_asesores = pd.DataFrame(rows_asesores, columns=cols_finales_asesor) if rows_asesores else pd.DataFrame(columns=cols_finales_asesor)

        cols_finales_tl = ['Team Leader', 'Monitoreos', 'TOTAL']
        df_tl = pd.DataFrame(rows_tl, columns=cols_finales_tl)

        if not df_asesores.empty:
            html_asesores = df_asesores.fillna('---').to_html(classes='table table-striped tabla-reporte', index=False, escape=False)
        else:
            html_asesores = '<p class="text-muted">No se encontraron registros de asesores para las líderes seleccionadas.</p>'

        html_tl = df_tl.to_html(classes='table table-bordered tabla-tl-custom', index=False, escape=False)
        html_tl_container = f'''
        <style>
            .tabla-tl-custom {{
                border: 2px solid #000 !important;
                text-align: center;
                font-weight: bold;
            }}
            .tabla-tl-custom th {{
                background-color: #F79646 !important;
                color: white !important;
                text-align: center !important;
                border: 1px solid #000 !important;
            }}
            .tabla-tl-custom td {{
                border: 1px solid #000 !important;
                vertical-align: middle !important;
            }}
        </style>
        <div style="display: flex; justify-content: flex-end; margin-bottom: 25px;">
            <div style="min-width: 420px;">
                {html_tl}
            </div>
        </div>
        '''

        return jsonify({
            "success": True,
            "message": "Planilla Resumen procesada correctamente.",
            "html_tabla": html_tl_container + html_asesores
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Detalle del error: {type(e).__name__} - {str(e)}"
        }), 400

if __name__ == '__main__':
    print("\n🚀 Servidor activo en http://127.0.0.1:5000\n")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)