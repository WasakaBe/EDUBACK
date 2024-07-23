from flask import Blueprint, jsonify, request
from Database.Database import db, TBL_ASISTENCIAS
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

asistencias_bp = Blueprint('asistencias_bp', __name__)

# Ruta para insertar una nueva asistencia
@asistencias_bp.route('/asistencias/insert', methods=['POST'])
def create_asistencia():
    data = request.get_json()
    id_alumno = data.get('id_alumno')
    id_horario = data.get('id_horario')
    fecha = data.get('fecha')
    estado_asistencia = data.get('estado_asistencia')
    comentarios = data.get('comentarios')

    if not all([id_alumno, id_horario, fecha, estado_asistencia]):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    new_asistencia = TBL_ASISTENCIAS(
        id_alumno=id_alumno,
        id_horario=id_horario,
        fecha=fecha,
        estado_asistencia=estado_asistencia,
        comentarios=comentarios
    )

    try:
        db.session.add(new_asistencia)
        db.session.commit()
        return jsonify({'message': 'Asistencia creada exitosamente'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para visualizar todas las asistencias
@asistencias_bp.route('/asistencias', methods=['GET'])
def get_all_asistencias():
    asistencias = TBL_ASISTENCIAS.query.all()
    result = [{
        'id_asistencia': asistencia.id_asistencia,
        'id_alumno': asistencia.id_alumno,
        'id_horario': asistencia.id_horario,
        'fecha': asistencia.fecha,
        'estado_asistencia': asistencia.estado_asistencia,
        'comentarios': asistencia.comentarios
    } for asistencia in asistencias]
    return jsonify(result), 200

# Ruta para visualizar una asistencia por su ID
@asistencias_bp.route('/asistencias/<int:id>', methods=['GET'])
def get_asistencia(id):
    asistencia = TBL_ASISTENCIAS.query.get(id)
    if not asistencia:
        return jsonify({'error': 'Asistencia no encontrada'}), 404
    return jsonify({
        'id_asistencia': asistencia.id_asistencia,
        'id_alumno': asistencia.id_alumno,
        'id_horario': asistencia.id_horario,
        'fecha': asistencia.fecha,
        'estado_asistencia': asistencia.estado_asistencia,
        'comentarios': asistencia.comentarios
    }), 200

# Ruta para actualizar una asistencia por su ID
@asistencias_bp.route('/asistencias/<int:id>', methods=['PUT'])
def update_asistencia(id):
    data = request.get_json()
    asistencia = TBL_ASISTENCIAS.query.get(id)

    if not asistencia:
        return jsonify({'error': 'Asistencia no encontrada'}), 404

    asistencia.id_alumno = data.get('id_alumno', asistencia.id_alumno)
    asistencia.id_horario = data.get('id_horario', asistencia.id_horario)
    asistencia.fecha = data.get('fecha', asistencia.fecha)
    asistencia.estado_asistencia = data.get('estado_asistencia', asistencia.estado_asistencia)
    asistencia.comentarios = data.get('comentarios', asistencia.comentarios)

    try:
        db.session.commit()
        return jsonify({'message': 'Asistencia actualizada exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para eliminar una asistencia por su ID
@asistencias_bp.route('/asistencias/<int:id>', methods=['DELETE'])
def delete_asistencia(id):
    asistencia = TBL_ASISTENCIAS.query.get(id)
    if not asistencia:
        return jsonify({'error': 'Asistencia no encontrada'}), 404

    try:
        db.session.delete(asistencia)
        db.session.commit()
        return jsonify({'message': 'Asistencia eliminada exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500