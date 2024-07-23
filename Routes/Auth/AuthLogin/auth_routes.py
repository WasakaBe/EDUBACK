import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import Blueprint, jsonify, request
from Database.Database import db, TBL_USUARIOS, BITACORA_SESION,TBL_TIPO_ROL
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode, b64decode

auth_bp = Blueprint('auth_bp', __name__)

def send_email(to, subject, user_name):
    remitente = os.getenv('USER')
    destinatario = to

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = remitente
    msg['To'] = destinatario

    with open('Templates/loginemail.html', 'r') as archivo:
        html_content = archivo.read()

    # Reemplaza la etiqueta {{user_name}} en el HTML con el nombre del usuario
    html_content = html_content.replace('{{user_name}}', user_name)

    msg.attach(MIMEText(html_content, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remitente, os.getenv('PWD'))

    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

@auth_bp.route('/check-email', methods=['POST'])
def check_email():
    data = request.get_json()
    email = data.get('correo_usuario')
    if not email:
        return jsonify({'error': 'Email es requerido'}), 400

    user = TBL_USUARIOS.query.filter_by(correo_usuario=email).first()
    if user:
        return jsonify({'exists': True}), 200
    return jsonify({'exists': False}), 404

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('correo_usuario')
    password = data.get('pwd_usuario')

    if not email or not password:
        return jsonify({'error': 'Email y contraseña son requeridos'}), 400

    user = TBL_USUARIOS.query.filter_by(correo_usuario=email).first()
    if not user or user.pwd_usuario != password:
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401

    # Aquí puedes enviar el correo electrónico después de iniciar sesión
    send_email(user.correo_usuario, 'Bienvenido de nuevo a la aplicación', user.nombre_usuario)

    # Aquí puedes agregar la lógica para la bitácora de sesiones
    try:
        new_sesion = BITACORA_SESION(
            id_usuario=user.id_usuario,
            nombre_usuario=user.nombre_usuario,
            correo_usuario=user.correo_usuario,
            fecha_inicio=datetime.now(),
            ip_usuario=request.remote_addr,
            url_solicitada=request.path
        )
        db.session.add(new_sesion)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

    return jsonify({
        'tbl_users': {
            'id_usuario': user.id_usuario,
            'nombre_usuario': user.nombre_usuario,
            'app_usuario': user.app_usuario,
            'apm_usuario': user.apm_usuario,
            'phone_usuario': user.phone_usuario,
            'correo_usuario': user.correo_usuario,
            'pwd_usuario': user.pwd_usuario,
            'idRol': user.idRol,
            'foto_usuario': b64encode(user.foto_usuario).decode('utf-8') if user.foto_usuario else None
        }
    }), 200


@auth_bp.route('/get-user', methods=['POST'])
def get_user():
    data = request.get_json()
    email = data.get('correo_usuario')
    if not email:
        return jsonify({'error': 'Email es requerido'}), 400

    user = TBL_USUARIOS.query.filter_by(correo_usuario=email).first()
    if user:
        return jsonify({
            'id_usuario': user.id_usuario,
            'nombre_usuario': user.nombre_usuario,
            'idRol': user.idRol,
            'correo_usuario': user.correo_usuario
        }), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404


@auth_bp.route('/get-user-alexa', methods=['POST'])
def get_user_alexa():
    data = request.get_json()
    email = data.get('correo_usuario')
    if not email:
        return jsonify({'error': 'Email es requerido'}), 400

    user = db.session.query(
        TBL_USUARIOS,
        TBL_TIPO_ROL.nombre_tipo_rol
    ).join(
        TBL_TIPO_ROL, TBL_USUARIOS.idRol == TBL_TIPO_ROL.id_tipo_rol
    ).filter(
        TBL_USUARIOS.correo_usuario == email
    ).first()

    if user:
        user_data = user[0]  # Datos del usuario
        tipo_rol = user[1]  # Tipo de rol

        return jsonify({
            'id_usuario': user_data.id_usuario,
            'nombre_usuario': user_data.nombre_usuario,
            'idRol': user_data.idRol,
            'tipo_rol': tipo_rol if tipo_rol else 'Sin rol',
            'correo_usuario': user_data.correo_usuario
        }), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404


# Ruta para actualizar el perfil del usuario
@auth_bp.route('/update-profile/<int:id>', methods=['PUT'])
def update_profile(id):
    data = request.get_json()
    usuario = TBL_USUARIOS.query.get(id)

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    nombre_usuario = data.get('nombre_usuario')
    app_usuario = data.get('app_usuario')
    apm_usuario = data.get('apm_usuario')
    correo_usuario = data.get('correo_usuario')
    pwd_usuario = data.get('pwd_usuario')
    foto_usuario = data.get('foto_usuario')

    if not nombre_usuario or not app_usuario or not correo_usuario or not pwd_usuario:
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    usuario.nombre_usuario = nombre_usuario
    usuario.app_usuario = app_usuario
    usuario.apm_usuario = apm_usuario
    usuario.correo_usuario = correo_usuario
    usuario.pwd_usuario = pwd_usuario

    if foto_usuario:
        usuario.foto_usuario = b64decode(foto_usuario.encode('utf-8'))

    try:
        db.session.commit()
        return jsonify({'message': 'Perfil actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el perfil: ' + str(e)}), 500