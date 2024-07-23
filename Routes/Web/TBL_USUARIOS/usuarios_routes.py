import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from flask import Blueprint, jsonify, request
from Database.Database import db, TBL_USUARIOS, BITACORA_USUARIOS
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode, b64decode

usuarios_bp = Blueprint('usuarios_bp', __name__)

# Función para enviar correo electrónico
def send_email(to, subject, user_name):
    remitente = os.getenv('USER')
    destinatario = to

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = remitente
    msg['To'] = destinatario

    with open('Templates/email.html', 'r') as archivo:
        html_content = archivo.read()

    html_content = html_content.replace('{{user_name}}', user_name)
    msg.attach(MIMEText(html_content, 'html'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(remitente, os.getenv('PWD'))
    server.sendmail(remitente, destinatario, msg.as_string())
    server.quit()

# Ruta para visualizar todos los usuarios
@usuarios_bp.route('/usuario', methods=['GET'])
def get_all_usuarios():
    try:
        usuarios = TBL_USUARIOS.query.all()
        result = [{
            'id_usuario': usuario.id_usuario,
            'nombre_usuario': usuario.nombre_usuario,
            'app_usuario': usuario.app_usuario,
            'apm_usuario': usuario.apm_usuario,
            'fecha_nacimiento_usuario': usuario.fecha_nacimiento_usuario,
            'token_usuario': usuario.token_usuario,
            'correo_usuario': usuario.correo_usuario,
            'pwd_usuario': usuario.pwd_usuario,
            'phone_usuario': usuario.phone_usuario,
            'ip_usuario': usuario.ip_usuario,
            'id_rol': usuario.idRol,
            'id_sexo': usuario.idSexo,
            'id_cuenta_activo': usuario.idCuentaActivo,
            'id_pregunta': usuario.idPregunta,
            'respuesta_pregunta': usuario.respuestaPregunta,
            'foto_usuario': b64encode(usuario.foto_usuario).decode('utf-8') if usuario.foto_usuario else None
        } for usuario in usuarios]
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Error de la base de datos: ' + str(e)}), 500

# Ruta para visualizar un usuario por su ID
@usuarios_bp.route('/usuario/<int:id>', methods=['GET'])
def get_usuario(id):
    try:
        usuario = TBL_USUARIOS.query.get(id)
        if not usuario:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify({
            'id_usuario': usuario.id_usuario,
            'nombre_usuario': usuario.nombre_usuario,
            'app_usuario': usuario.app_usuario,
            'apm_usuario': usuario.apm_usuario,
            'fecha_nacimiento_usuario': usuario.fecha_nacimiento_usuario,
            'token_usuario': usuario.token_usuario,
            'correo_usuario': usuario.correo_usuario,
            'pwd_usuario': usuario.pwd_usuario,
            'phone_usuario': usuario.phone_usuario,
            'ip_usuario': usuario.ip_usuario,
            'id_rol': usuario.idRol,
            'id_sexo': usuario.idSexo,
            'id_cuenta_activo': usuario.idCuentaActivo,
            'id_pregunta': usuario.idPregunta,
            'respuesta_pregunta': usuario.respuestaPregunta,
            'foto_usuario': b64encode(usuario.foto_usuario).decode('utf-8') if usuario.foto_usuario else None
        }), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Error de la base de datos: ' + str(e)}), 500

# Ruta para actualizar un usuario por su ID
@usuarios_bp.route('/usuario/<int:id>', methods=['PUT'])
def update_usuario(id):
    data = request.get_json()
    usuario = TBL_USUARIOS.query.get(id)

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    nombre_usuario = data.get('nombre_usuario')
    app_usuario = data.get('app_usuario')
    apm_usuario = data.get('apm_usuario')
    fecha_nacimiento_usuario = data.get('fecha_nacimiento_usuario')
    token_usuario = data.get('token_usuario')
    correo_usuario = data.get('correo_usuario')
    pwd_usuario = data.get('pwd_usuario')
    phone_usuario = data.get('phone_usuario')
    ip_usuario = data.get('ip_usuario')
    id_rol = data.get('id_rol')
    id_sexo = data.get('id_sexo')
    id_cuenta_activo = data.get('id_cuenta_activo')
    id_pregunta = data.get('id_pregunta')
    respuesta_pregunta = data.get('respuesta_pregunta')
    foto_usuario = data.get('foto_usuario')

    if not nombre_usuario or not app_usuario or not token_usuario or not correo_usuario or not pwd_usuario:
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    usuario.nombre_usuario = nombre_usuario
    usuario.app_usuario = app_usuario
    usuario.apm_usuario = apm_usuario
    usuario.fecha_nacimiento_usuario = fecha_nacimiento_usuario
    usuario.token_usuario = token_usuario
    usuario.correo_usuario = correo_usuario
    usuario.pwd_usuario = pwd_usuario
    usuario.phone_usuario = phone_usuario
    usuario.ip_usuario = ip_usuario
    usuario.idRol = id_rol
    usuario.idSexo = id_sexo
    usuario.idCuentaActivo = id_cuenta_activo
    usuario.idPregunta = id_pregunta
    usuario.respuestaPregunta = respuesta_pregunta
    if foto_usuario:
        usuario.foto_usuario = b64decode(foto_usuario.encode('utf-8'))

    try:
        db.session.commit()

        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=usuario.id_usuario,
            nombre_usuario=usuario.nombre_usuario,
            accion_realizada='Actualización',
            detalles_accion='Usuario actualizado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Usuario actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error al actualizar el usuario: ' + str(e)}), 500

# Ruta para eliminar un usuario por su ID
@usuarios_bp.route('/usuario/<int:id>', methods=['DELETE'])
def delete_usuario(id):
    usuario = TBL_USUARIOS.query.get(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    try:
        db.session.delete(usuario)
        db.session.commit()

        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=usuario.id_usuario,
            nombre_usuario=usuario.nombre_usuario,
            accion_realizada='Eliminación',
            detalles_accion='Usuario eliminado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar el usuario: ' + str(e)}), 500
