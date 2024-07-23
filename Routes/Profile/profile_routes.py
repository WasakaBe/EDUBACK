from flask import Blueprint, jsonify, request, Response, current_app
from werkzeug.utils import secure_filename
from Database.Database import db, TBL_USUARIOS, BITACORA_USUARIOS
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from base64 import b64encode, b64decode
import os

profile_bp = Blueprint('profile_bp', __name__)

def log_action(user, action, details):
    max_length = 255  # Tamaño máximo permitido para `accion_realizada` y `detalles_accion`
    truncated_action = action[:max_length]
    truncated_details = details[:max_length] if details else None

    bitacora_entry = BITACORA_USUARIOS(
        id_usuario=user.id_usuario,
        nombre_usuario=user.nombre_usuario,
        accion_realizada=truncated_action,
        detalles_accion=truncated_details,
        fecha_acceso=datetime.now(),
        ip_acceso=request.remote_addr
    )
    db.session.add(bitacora_entry)
    db.session.commit()

@profile_bp.route('/update4-user/<int:id>', methods=['POST'])
def update_user(id):
    user = TBL_USUARIOS.query.get(id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    try:
        data = request.form
        nombre_usuario = data.get('nombre_usuario')
        app_usuario = data.get('app_usuario')
        apm_usuario = data.get('apm_usuario')
        phone_usuario = data.get('phone_usuario')
        correo_usuario = data.get('correo_usuario')
        pwd_usuario = data.get('pwd_usuario')
        file = request.files.get('image')

        if nombre_usuario:
            user.nombre_usuario = nombre_usuario
        if app_usuario:
            user.app_usuario = app_usuario
        if apm_usuario:
            user.apm_usuario = apm_usuario
        if phone_usuario:
            user.phone_usuario = phone_usuario
        if correo_usuario:
            user.correo_usuario = correo_usuario
        if pwd_usuario:
            user.pwd_usuario = pwd_usuario

        # Manejar la subida de la imagen si se proporciona
        if file:
            if file.filename == '':
                return jsonify({'message': 'No file selected for uploading'}), 400

            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            with open(file_path, 'rb') as file:
                binary_data = file.read()

            user.foto_usuario = binary_data

        db.session.commit()
        log_action(user, 'Actualización de perfil', 'Perfil actualizado correctamente')
        return jsonify({'message': 'Datos de usuario actualizados exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error al actualizar los datos del usuario: {str(e)}")  # Imprimir el error en los logs
        return jsonify({'error': 'Error en la base de datos. Por favor intente nuevamente.'}), 500
    except Exception as e:
        db.session.rollback()
        print(f"Error general: {str(e)}")  # Imprimir el error en los logs
        return jsonify({'error': 'Ocurrió un error inesperado. Por favor intente nuevamente.'}), 500

@profile_bp.route('/get-user/<int:id>', methods=['GET'])
def get_user(id):
    user = TBL_USUARIOS.query.get(id)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    return jsonify({
        'id_usuario': user.id_usuario,
        'nombre_usuario': user.nombre_usuario,
        'app_usuario': user.app_usuario,
        'apm_usuario': user.apm_usuario,
        'phone_usuario': user.phone_usuario,
        'correo_usuario': user.correo_usuario,
        'pwd_usuario': user.pwd_usuario,
        'foto_usuario': b64encode(user.foto_usuario).decode('utf-8') if user.foto_usuario else None
    }), 200

@profile_bp.route('/profile-image/<int:id>', methods=['GET'])
def profile_image(id):
    user = TBL_USUARIOS.query.get(id)
    if not user or not user.foto_usuario:
        return jsonify({'message': 'Usuario o imagen no encontrados'}), 404
    return Response(user.foto_usuario, mimetype='image/jpeg')
