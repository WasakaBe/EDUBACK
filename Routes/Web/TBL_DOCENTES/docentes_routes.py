import os
from datetime import datetime
from flask import Blueprint, jsonify, request
from Database.Database import db, TBL_DOCENTES, BITACORA_USUARIOS
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode, b64decode

docentes_bp = Blueprint('docentes_bp', __name__)

# Ruta para insertar un nuevo docente
@docentes_bp.route('/docente/insert', methods=['POST'])
def create_docente():
    data = request.get_json()
    nombre_docentes = data.get('nombre_docentes')
    app_docentes = data.get('app_docentes')
    apm_docentes = data.get('apm_docentes')
    fecha_nacimiento_docentes = data.get('fecha_nacimiento_docentes')
    noconttrol_docentes = data.get('noconttrol_docentes')
    telefono_docentes = data.get('telefono_docentes')
    foto_docentes = data.get('foto_docentes')
    seguro_social_docentes = data.get('seguro_social_docentes')
    idSexo = data.get('idSexo')
    idUsuario = data.get('idUsuario')
    idClinica = data.get('idClinica')

    if not all([nombre_docentes, app_docentes, apm_docentes, fecha_nacimiento_docentes, noconttrol_docentes, telefono_docentes, seguro_social_docentes]):
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    new_docente = TBL_DOCENTES(
        nombre_docentes=nombre_docentes,
        app_docentes=app_docentes,
        apm_docentes=apm_docentes,
        fecha_nacimiento_docentes=fecha_nacimiento_docentes,
        noconttrol_docentes=noconttrol_docentes,
        telefono_docentes=telefono_docentes,
        foto_docentes=b64decode(foto_docentes.encode('utf-8')) if foto_docentes else None,
        seguro_social_docentes=seguro_social_docentes,
        idSexo=idSexo,
        idUsuario=idUsuario,
        idClinica=idClinica
    )

    try:
        db.session.add(new_docente)
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=idUsuario,
            nombre_usuario=new_docente.nombre_docentes,
            accion_realizada='Registro',
            detalles_accion='Docente registrado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Docente creado exitosamente'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para visualizar todos los docentes
@docentes_bp.route('/docente', methods=['GET'])
def get_all_docentes():
    try:
        docentes = TBL_DOCENTES.query.all()
        result = [{
            'id_docentes': docente.id_docentes,
            'nombre_docentes': docente.nombre_docentes,
            'app_docentes': docente.app_docentes,
            'apm_docentes': docente.apm_docentes,
            'fecha_nacimiento_docentes': docente.fecha_nacimiento_docentes.isoformat(),
            'noconttrol_docentes': docente.noconttrol_docentes,
            'telefono_docentes': docente.telefono_docentes,
            'foto_docentes': b64encode(docente.foto_docentes).decode('utf-8') if docente.foto_docentes else None,
            'seguro_social_docentes': docente.seguro_social_docentes,
            'idSexo': docente.idSexo,
            'idUsuario': docente.idUsuario,
            'idClinica': docente.idClinica
        } for docente in docentes]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener los docentes', 'error': str(e)}), 500



# Ruta para visualizar un docente por su ID
@docentes_bp.route('/docente/<int:id>', methods=['GET'])
def get_docente(id):
    docente = TBL_DOCENTES.query.get(id)
    if not docente:
        return jsonify({'error': 'Docente no encontrado'}), 404
    return jsonify({
        'id_docentes': docente.id_docentes,
        'nombre_docentes': docente.nombre_docentes,
        'app_docentes': docente.app_docentes,
        'apm_docentes': docente.apm_docentes,
        'fecha_nacimiento_docentes': docente.fecha_nacimiento_docentes.isoformat(),
        'noconttrol_docentes': docente.noconttrol_docentes,
        'telefono_docentes': docente.telefono_docentes,
        'foto_docentes': b64encode(docente.foto_docentes).decode('utf-8') if docente.foto_docentes else None,
        'seguro_social_docentes': docente.seguro_social_docentes,
        'idSexo': docente.idSexo,
        'idUsuario': docente.idUsuario,
        'idClinica': docente.idClinica
    }), 200

# Nueva ruta para visualizar un docente por su número de control o CURP
@docentes_bp.route('/docentes/nocontrol/<string:nocontrol>', methods=['GET'])
def get_docente_by_nocontrol(nocontrol):
    docente = TBL_DOCENTES.query.filter_by(noconttrol_docentes=nocontrol).first()
    if not docente:
        return jsonify({'error': 'Docente no encontrado'}), 404
    return jsonify({
        'id_docentes': docente.id_docentes,
        'nombre_docentes': docente.nombre_docentes,
        'app_docentes': docente.app_docentes,
        'apm_docentes': docente.apm_docentes,
        'fecha_nacimiento_docentes': docente.fecha_nacimiento_docentes.isoformat(),
        'noconttrol_docentes': docente.noconttrol_docentes,
        'telefono_docentes': docente.telefono_docentes,
        'foto_docentes': b64encode(docente.foto_docentes).decode('utf-8') if docente.foto_docentes else None,
        'seguro_social_docentes': docente.seguro_social_docentes,
        'idSexo': docente.idSexo,
        'idUsuario': docente.idUsuario,
        'idClinica': docente.idClinica
    }), 200

# Ruta para actualizar un docente por su ID
@docentes_bp.route('/docente/<int:id>', methods=['PUT'])
def update_docente(id):
    data = request.get_json()
    docente = TBL_DOCENTES.query.get(id)

    if not docente:
        return jsonify({'error': 'Docente no encontrado'}), 404

    nombre_docentes = data.get('nombre_docentes')
    app_docentes = data.get('app_docentes')
    apm_docentes = data.get('apm_docentes')
    fecha_nacimiento_docentes = data.get('fecha_nacimiento_docentes')
    noconttrol_docentes = data.get('noconttrol_docentes')
    telefono_docentes = data.get('telefono_docentes')
    foto_docentes = data.get('foto_docentes')
    seguro_social_docentes = data.get('seguro_social_docentes')
    idSexo = data.get('idSexo')
    idUsuario = data.get('idUsuario')
    idClinica = data.get('idClinica')

    if not all([nombre_docentes, app_docentes, apm_docentes, fecha_nacimiento_docentes, noconttrol_docentes, telefono_docentes, seguro_social_docentes]):
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    docente.nombre_docentes = nombre_docentes
    docente.app_docentes = app_docentes
    docente.apm_docentes = apm_docentes
    docente.fecha_nacimiento_docentes = fecha_nacimiento_docentes
    docente.noconttrol_docentes = noconttrol_docentes
    docente.telefono_docentes = telefono_docentes
    if foto_docentes:
        docente.foto_docentes = b64decode(foto_docentes.encode('utf-8'))
    docente.seguro_social_docentes = seguro_social_docentes
    docente.idSexo = idSexo
    docente.idUsuario = idUsuario
    docente.idClinica = idClinica

    try:
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=idUsuario,
            nombre_usuario=docente.nombre_docentes,
            accion_realizada='Actualización',
            detalles_accion='Docente actualizado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Docente actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para eliminar un docente por su ID
@docentes_bp.route('/docente/<int:id>', methods=['DELETE'])
def delete_docente(id):
    docente = TBL_DOCENTES.query.get(id)
    if not docente:
        return jsonify({'error': 'Docente no encontrado'}), 404

    try:
        db.session.delete(docente)
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=docente.idUsuario,
            nombre_usuario=docente.nombre_docentes,
            accion_realizada='Eliminación',
            detalles_accion='Docente eliminado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Docente eliminado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
