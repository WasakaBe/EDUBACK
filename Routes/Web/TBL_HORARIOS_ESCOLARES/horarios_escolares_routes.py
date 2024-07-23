from flask import Blueprint, app, jsonify, request
from Database.Database import  db, TBL_ASIGNATURAS, TBL_CARRERAS_TECNICAS, TBL_DOCENTES, TBL_GRADOS, TBL_GRUPOS, TBL_HORARIOS_ESCOLARES
from sqlalchemy.exc import SQLAlchemyError

horarios_escolares_bp = Blueprint('horarios_escolares_bp', __name__)

# Ruta para insertar un nuevo horario escolar
@horarios_escolares_bp.route('/horarios_escolares/insert', methods=['POST'])
def create_horario_escolar():
    data = request.get_json()
    id_asignatura = data.get('id_asignatura')
    id_docente = data.get('id_docente')
    id_grado = data.get('id_grado')
    id_grupo = data.get('id_grupo')
    id_carrera_tecnica = data.get('id_carrera_tecnica')
    ciclo_escolar = data.get('ciclo_escolar')
    dias_horarios = data.get('dias_horarios')

    if not all([id_asignatura, id_docente, id_grado, id_grupo, id_carrera_tecnica, ciclo_escolar, dias_horarios]):
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    try:
        # Verificar conflictos de horarios
        existing_horarios = db.session.query(TBL_HORARIOS_ESCOLARES).filter(
            TBL_HORARIOS_ESCOLARES.id_docente == id_docente,
            TBL_HORARIOS_ESCOLARES.ciclo_escolar == ciclo_escolar
        ).all()

        for horario in existing_horarios:
            existing_dias_horarios = eval(horario.dias_horarios)
            for new_dia in dias_horarios:
                for existing_dia in existing_dias_horarios:
                    if new_dia['day'] == existing_dia['day']:
                        if not (new_dia['endTime'] <= existing_dia['startTime'] or new_dia['startTime'] >= existing_dia['endTime']):
                            return jsonify({'error': 'Conflicto de horario detectado'}), 409

        # Crear el nuevo horario
        new_horario = TBL_HORARIOS_ESCOLARES(
            id_asignatura=id_asignatura,
            id_docente=id_docente,
            id_grado=id_grado,
            id_grupo=id_grupo,
            id_carrera_tecnica=id_carrera_tecnica,
            ciclo_escolar=ciclo_escolar,
            dias_horarios=str(dias_horarios)  # Asegúrate de almacenar como string
        )

        db.session.add(new_horario)
        db.session.commit()
        return jsonify({'message': 'Horario escolar creado exitosamente'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para visualizar todos los horarios escolares
@horarios_escolares_bp.route('/horarios_escolares', methods=['GET'])
def get_all_horarios_escolares():
    try:
        horarios = db.session.query(
            TBL_HORARIOS_ESCOLARES.id_horario,
            TBL_ASIGNATURAS.nombre_asignatura,
            TBL_DOCENTES.nombre_docentes,
            TBL_DOCENTES.app_docentes,
            TBL_DOCENTES.apm_docentes,
            TBL_GRADOS.nombre_grado,
            TBL_GRUPOS.nombre_grupos,
            TBL_CARRERAS_TECNICAS.nombre_carrera_tecnica,
            TBL_HORARIOS_ESCOLARES.ciclo_escolar,
            TBL_HORARIOS_ESCOLARES.dias_horarios
        ).join(TBL_ASIGNATURAS, TBL_ASIGNATURAS.id_asignatura == TBL_HORARIOS_ESCOLARES.id_asignatura)\
         .join(TBL_DOCENTES, TBL_DOCENTES.id_docentes == TBL_HORARIOS_ESCOLARES.id_docente)\
         .join(TBL_GRADOS, TBL_GRADOS.id_grado == TBL_HORARIOS_ESCOLARES.id_grado)\
         .join(TBL_GRUPOS, TBL_GRUPOS.id_grupos == TBL_HORARIOS_ESCOLARES.id_grupo)\
         .join(TBL_CARRERAS_TECNICAS, TBL_CARRERAS_TECNICAS.id_carrera_tecnica == TBL_HORARIOS_ESCOLARES.id_carrera_tecnica)\
         .all()

        result = [{
            'id_horario': horario.id_horario,
            'nombre_asignatura': horario.nombre_asignatura,
            'nombre_docente': f"{horario.nombre_docentes} {horario.app_docentes} {horario.apm_docentes}",
            'nombre_grado': horario.nombre_grado,
            'nombre_grupo': horario.nombre_grupos,
            'nombre_carrera_tecnica': horario.nombre_carrera_tecnica,
            'ciclo_escolar': horario.ciclo_escolar,
            'dias_horarios': eval(horario.dias_horarios) if horario.dias_horarios else []
        } for horario in horarios]

        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# Ruta para actualizar un horario escolar
@horarios_escolares_bp.route('/horarios_escolares/update/<int:id>', methods=['PUT'])
def update_horario_escolar(id):
    data = request.get_json()
    try:
        horario = TBL_HORARIOS_ESCOLARES.query.get(id)
        if not horario:
            return jsonify({'error': 'Horario no encontrado'}), 404

        horario.id_asignatura = data.get('id_asignatura')
        horario.id_docente = data.get('id_docente')
        horario.id_grado = data.get('id_grado')
        horario.id_grupo = data.get('id_grupo')
        horario.id_carrera_tecnica = data.get('id_carrera_tecnica')
        horario.ciclo_escolar = data.get('ciclo_escolar')
        horario.dias_horarios = str(data.get('dias_horarios'))  # Asegúrate de almacenar como string

        db.session.commit()
        return jsonify({'message': 'Horario actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        app.logger.error(f"Error de SQLAlchemy: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Error inesperado: {str(e)}")
        return jsonify({'error': str(e)}), 500
