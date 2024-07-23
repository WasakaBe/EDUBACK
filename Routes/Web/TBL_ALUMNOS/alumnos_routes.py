import os
from datetime import datetime
from flask import Blueprint,  jsonify, request, current_app as app
from Database.Database import TBL_CARRERAS_TECNICAS, TBL_CLINICAS, TBL_ESTADOS, TBL_GRADOS, TBL_GRUPOS, TBL_PAISES, TBL_SEXOS, TBL_USUARIOS, db, TBL_ALUMNOS, BITACORA_USUARIOS
from sqlalchemy.exc import SQLAlchemyError
from base64 import b64encode, b64decode

alumnos_bp = Blueprint('alumnos_bp', __name__)

# Ruta para insertar un nuevo alumno
@alumnos_bp.route('/alumno/insert', methods=['POST'])
def create_alumno():
    data = request.get_json()
    nombre_alumnos = data.get('nombre_alumnos')
    app_alumnos = data.get('app_alumnos')
    apm_alumnos = data.get('apm_alumnos')
    foto_alumnos = data.get('foto_alumnos')
    fecha_nacimiento_alumnos = data.get('fecha_nacimiento_alumnos')
    curp_alumnos = data.get('curp_alumnos')
    nocontrol_alumnos = data.get('nocontrol_alumnos')
    telefono_alumnos = data.get('telefono_alumnos')
    seguro_social_alumnos = data.get('seguro_social_alumnos')
    cuentacredencial_alumnos = data.get('cuentacredencial_alumnos')
    id_sexo = data.get('id_sexo')
    id_usuario = data.get('id_usuario')
    id_clinica = data.get('id_clinica')
    id_grado = data.get('id_grado')
    id_grupo = data.get('id_grupo')
    id_traslado = data.get('id_traslado')
    id_trasladotransporte = data.get('id_trasladotransporte')
    id_carrera_tecnica = data.get('id_carrera_tecnica')
    id_pais = data.get('id_pais')
    id_estado = data.get('id_estado')
    municipio_alumnos = data.get('municipio_alumnos')
    comunidad_alumnos = data.get('comunidad_alumnos')
    calle_alumnos = data.get('calle_alumnos')
    proc_sec_alumno = data.get('proc_sec_alumno')

    if not nombre_alumnos or not app_alumnos or not apm_alumnos or not fecha_nacimiento_alumnos or not curp_alumnos or not nocontrol_alumnos or not telefono_alumnos or not seguro_social_alumnos or not cuentacredencial_alumnos:
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    new_alumno = TBL_ALUMNOS(
        nombre_alumnos=nombre_alumnos,
        app_alumnos=app_alumnos,
        apm_alumnos=apm_alumnos,
        foto_alumnos=b64decode(foto_alumnos.encode('utf-8')) if foto_alumnos else None,
        fecha_nacimiento_alumnos=fecha_nacimiento_alumnos,
        curp_alumnos=curp_alumnos,
        nocontrol_alumnos=nocontrol_alumnos,
        telefono_alumnos=telefono_alumnos,
        seguro_social_alumnos=seguro_social_alumnos,
        cuentacredencial_alumnos=cuentacredencial_alumnos,
        id_sexo=id_sexo,
        id_usuario=id_usuario,
        id_clinica=id_clinica,
        id_grado=id_grado,
        id_grupo=id_grupo,
        id_traslado=id_traslado,
        id_trasladotransporte=id_trasladotransporte,
        id_carrera_tecnica=id_carrera_tecnica,
        id_pais=id_pais,
        id_estado=id_estado,
        municipio_alumnos=municipio_alumnos,
        comunidad_alumnos=comunidad_alumnos,
        calle_alumnos=calle_alumnos,
        proc_sec_alumno=proc_sec_alumno
    )

    try:
        db.session.add(new_alumno)
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=id_usuario,
            nombre_usuario=new_alumno.nombre_alumnos,
            accion_realizada='Registro',
            detalles_accion='Alumno registrado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Alumno creado exitosamente'}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para visualizar todos los alumnos
@alumnos_bp.route('/alumno', methods=['GET'])
def get_all_alumnos():
    alumnos = TBL_ALUMNOS.query.all()
    result = [{
        'id_alumnos': alumno.id_alumnos,
        'nombre_alumnos': alumno.nombre_alumnos,
        'app_alumnos': alumno.app_alumnos,
        'apm_alumnos': alumno.apm_alumnos,
        'foto_alumnos': b64encode(alumno.foto_alumnos).decode('utf-8') if alumno.foto_alumnos else None,
        'fecha_nacimiento_alumnos': alumno.fecha_nacimiento_alumnos,
        'curp_alumnos': alumno.curp_alumnos,
        'nocontrol_alumnos': alumno.nocontrol_alumnos,
        'telefono_alumnos': alumno.telefono_alumnos,
        'seguro_social_alumnos': alumno.seguro_social_alumnos,
        'cuentacredencial_alumnos': alumno.cuentacredencial_alumnos,
        'idSexo': alumno.idSexo,
        'idUsuario': alumno.idUsuario,
        'idClinica': alumno.idClinica,
        'idGrado': alumno.idGrado,
        'idGrupo': alumno.idGrupo,
        'idTraslado': alumno.idTraslado,
        'idTrasladotransporte': alumno.idTrasladotransporte,
        'idCarreraTecnica': alumno.idCarreraTecnica,
        'idPais': alumno.idPais,
        'idEstado': alumno.idEstado,
        'municipio_alumnos': alumno.municipio_alumnos,
        'comunidad_alumnos': alumno.comunidad_alumnos,
        'calle_alumnos': alumno.calle_alumnos,
        'proc_sec_alumno': alumno.proc_sec_alumno
    } for alumno in alumnos]
    return jsonify(result), 200

# Ruta para visualizar un alumno por su ID
@alumnos_bp.route('/alumno/<int:id>', methods=['GET'])
def get_alumno(id):
    alumno = TBL_ALUMNOS.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    return jsonify({
        'id_alumnos': alumno.id_alumnos,
        'nombre_alumnos': alumno.nombre_alumnos,
        'app_alumnos': alumno.app_alumnos,
        'apm_alumnos': alumno.apm_alumnos,
        'foto_alumnos': b64encode(alumno.foto_alumnos).decode('utf-8') if alumno.foto_alumnos else None,
        'fecha_nacimiento_alumnos': alumno.fecha_nacimiento_alumnos,
        'curp_alumnos': alumno.curp_alumnos,
        'nocontrol_alumnos': alumno.nocontrol_alumnos,
        'telefono_alumnos': alumno.telefono_alumnos,
        'seguro_social_alumnos': alumno.seguro_social_alumnos,
        'cuentacredencial_alumnos': alumno.cuentacredencial_alumnos,
        'idSexo': alumno.idSexo,
        'idUsuario': alumno.idUsuario,
        'idClinica': alumno.idClinica,
        'idGrado': alumno.idGrado,
        'idGrupo': alumno.idGrupo,
        'idTraslado': alumno.idTraslado,
        'idTrasladotransporte': alumno.idTrasladotransporte,
        'idCarreraTecnica': alumno.idCarreraTecnica,
        'idPais': alumno.idPais,
        'idEstado': alumno.idEstado,
        'municipio_alumnos': alumno.municipio_alumnos,
        'comunidad_alumnos': alumno.comunidad_alumnos,
        'calle_alumnos': alumno.calle_alumnos,
        'proc_sec_alumno': alumno.proc_sec_alumno
    }), 200

# Ruta para actualizar un alumno por su ID
@alumnos_bp.route('/alumno/<int:id>', methods=['PUT'])
def update_alumno(id):
    data = request.get_json()
    alumno = TBL_ALUMNOS.query.get(id)

    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    nombre_alumnos = data.get('nombre_alumnos')
    app_alumnos = data.get('app_alumnos')
    apm_alumnos = data.get('apm_alumnos')
    foto_alumnos = data.get('foto_alumnos')
    fecha_nacimiento_alumnos = data.get('fecha_nacimiento_alumnos')
    curp_alumnos = data.get('curp_alumnos')
    nocontrol_alumnos = data.get('nocontrol_alumnos')
    telefono_alumnos = data.get('telefono_alumnos')
    seguro_social_alumnos = data.get('seguro_social_alumnos')
    cuentacredencial_alumnos = data.get('cuentacredencial_alumnos')
    id_sexo = data.get('id_sexo')
    id_usuario = data.get('id_usuario')
    id_clinica = data.get('id_clinica')
    id_grado = data.get('id_grado')
    id_grupo = data.get('id_grupo')
    id_traslado = data.get('id_traslado')
    id_trasladotransporte = data.get('id_trasladotransporte')
    id_carrera_tecnica = data.get('id_carrera_tecnica')
    id_pais = data.get('id_pais')
    id_estado = data.get('id_estado')
    municipio_alumnos = data.get('municipio_alumnos')
    comunidad_alumnos = data.get('comunidad_alumnos')
    calle_alumnos = data.get('calle_alumnos')
    proc_sec_alumno = data.get('proc_sec_alumno')

    if not nombre_alumnos or not app_alumnos or not apm_alumnos or not fecha_nacimiento_alumnos or not curp_alumnos or not nocontrol_alumnos or not telefono_alumnos or not seguro_social_alumnos or not cuentacredencial_alumnos:
        return jsonify({'error': 'Los campos obligatorios no pueden estar vacíos'}), 400

    alumno.nombre_alumnos = nombre_alumnos
    alumno.app_alumnos = app_alumnos
    alumno.apm_alumnos = apm_alumnos
    if foto_alumnos:
        alumno.foto_alumnos = b64decode(foto_alumnos.encode('utf-8'))
    alumno.fecha_nacimiento_alumnos = fecha_nacimiento_alumnos
    alumno.curp_alumnos = curp_alumnos
    alumno.nocontrol_alumnos = nocontrol_alumnos
    alumno.telefono_alumnos = telefono_alumnos
    alumno.seguro_social_alumnos = seguro_social_alumnos
    alumno.cuentacredencial_alumnos = cuentacredencial_alumnos
    alumno.id_sexo = id_sexo
    alumno.id_usuario = id_usuario
    alumno.id_clinica = id_clinica
    alumno.id_grado = id_grado
    alumno.id_grupo = id_grupo
    alumno.id_traslado = id_traslado
    alumno.id_trasladotransporte = id_trasladotransporte
    alumno.id_carrera_tecnica = id_carrera_tecnica
    alumno.id_pais = id_pais
    alumno.id_estado = id_estado
    alumno.municipio_alumnos = municipio_alumnos
    alumno.comunidad_alumnos = comunidad_alumnos
    alumno.calle_alumnos = calle_alumnos
    alumno.proc_sec_alumno = proc_sec_alumno

    try:
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=id_usuario,
            nombre_usuario=alumno.nombre_alumnos,
            accion_realizada='Actualización',
            detalles_accion='Alumno actualizado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Alumno actualizado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para eliminar un alumno por su ID
@alumnos_bp.route('/alumno/<int:id>', methods=['DELETE'])
def delete_alumno(id):
    alumno = TBL_ALUMNOS.query.get(id)
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    try:
        db.session.delete(alumno)
        db.session.commit()

        # Insertar un nuevo registro en BITACORA_USUARIOS
        user_ip = request.remote_addr
        new_bitacora = BITACORA_USUARIOS(
            id_usuario=alumno.id_usuario,
            nombre_usuario=alumno.nombre_alumnos,
            accion_realizada='Eliminación',
            detalles_accion='Alumno eliminado exitosamente',
            fecha_acceso=datetime.now(),
            ip_acceso=user_ip
        )
        db.session.add(new_bitacora)
        db.session.commit()

        return jsonify({'message': 'Alumno eliminado exitosamente'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Ruta para buscar un alumno por su número de control
@alumnos_bp.route('/alumnos/nocontrol/<string:nocontrol>', methods=['GET'])
def get_alumno_by_nocontrol(nocontrol):
    alumno = db.session.query(
        TBL_ALUMNOS, 
        TBL_SEXOS.nombre_sexo, 
        TBL_CLINICAS.nombre_clinicas, 
        TBL_CARRERAS_TECNICAS.nombre_carrera_tecnica,
        TBL_CARRERAS_TECNICAS.foto_carrera_tecnica,  # Incluir foto de la carrera técnica
        TBL_GRADOS.nombre_grado,
        TBL_GRUPOS.nombre_grupos,
        TBL_PAISES.nombre_pais,
        TBL_ESTADOS.nombre_estado,
        TBL_USUARIOS.correo_usuario,
        TBL_USUARIOS.foto_usuario  # Incluir foto del usuario
    )\
    .join(TBL_SEXOS, TBL_ALUMNOS.idSexo == TBL_SEXOS.id_sexos)\
    .join(TBL_CLINICAS, TBL_ALUMNOS.idClinica == TBL_CLINICAS.id_clinicas)\
    .join(TBL_CARRERAS_TECNICAS, TBL_ALUMNOS.idCarreraTecnica == TBL_CARRERAS_TECNICAS.id_carrera_tecnica)\
    .join(TBL_GRADOS, TBL_ALUMNOS.idGrado == TBL_GRADOS.id_grado)\
    .join(TBL_GRUPOS, TBL_ALUMNOS.idGrupo == TBL_GRUPOS.id_grupos)\
    .join(TBL_PAISES, TBL_ALUMNOS.idPais == TBL_PAISES.id_pais)\
    .join(TBL_ESTADOS, TBL_ALUMNOS.idEstado == TBL_ESTADOS.id_estado)\
    .join(TBL_USUARIOS, TBL_ALUMNOS.idUsuario == TBL_USUARIOS.id_usuario)\
    .filter(TBL_ALUMNOS.nocontrol_alumnos == nocontrol).first()

    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404

    alumno_data = alumno[0]
    nombre_sexo = alumno[1]
    nombre_clinica = alumno[2]
    nombre_carrera_tecnica = alumno[3]
    foto_carrera_tecnica = alumno[4]  # Foto de la carrera técnica
    nombre_grado = alumno[5]
    nombre_grupo = alumno[6]
    nombre_pais = alumno[7]
    nombre_estado = alumno[8]
    correo_usuario = alumno[9]
    foto_usuario = alumno[10]  # Foto del usuario

    return jsonify({
        'id_alumnos': alumno_data.id_alumnos,
        'nombre_alumnos': alumno_data.nombre_alumnos,
        'app_alumnos': alumno_data.app_alumnos,
        'apm_alumnos': alumno_data.apm_alumnos,
        'foto_usuario': b64encode(foto_usuario).decode('utf-8') if foto_usuario else None,  # Utilizar foto del usuario
        'foto_carrera_tecnica': b64encode(foto_carrera_tecnica).decode('utf-8') if foto_carrera_tecnica else None,  # Utilizar foto de la carrera técnica
        'fecha_nacimiento_alumnos': alumno_data.fecha_nacimiento_alumnos,
        'curp_alumnos': alumno_data.curp_alumnos,
        'nocontrol_alumnos': alumno_data.nocontrol_alumnos,
        'telefono_alumnos': alumno_data.telefono_alumnos,
        'seguro_social_alumnos': alumno_data.seguro_social_alumnos,
        'cuentacredencial_alumnos': alumno_data.cuentacredencial_alumnos,
        'sexo': nombre_sexo,
        'correo_usuario': correo_usuario,
        'clinica': nombre_clinica,
        'grado': nombre_grado,
        'grupo': nombre_grupo,
        'traslado': alumno_data.idTraslado,
        'traslado_transporte': alumno_data.idTrasladotransporte,
        'carrera_tecnica': nombre_carrera_tecnica,
        'pais': nombre_pais,
        'estado': nombre_estado,
        'municipio_alumnos': alumno_data.municipio_alumnos,
        'comunidad_alumnos': alumno_data.comunidad_alumnos,
        'calle_alumnos': alumno_data.calle_alumnos,
        'proc_sec_alumno': alumno_data.proc_sec_alumno
    }), 200


# Ruta para obtener la información del alumno relacionado con el usuario logueado
@alumnos_bp.route('/alumno/usuario/<int:id_usuario>', methods=['GET'])
def get_alumno_by_usuario(id_usuario):
    alumno = db.session.query(
        TBL_ALUMNOS, 
        TBL_SEXOS.nombre_sexo, 
        TBL_CLINICAS.nombre_clinicas, 
        TBL_CARRERAS_TECNICAS.nombre_carrera_tecnica,
        TBL_CARRERAS_TECNICAS.foto_carrera_tecnica,  # Añadir foto de la carrera técnica
        TBL_GRADOS.nombre_grado,
        TBL_GRUPOS.nombre_grupos,
        TBL_PAISES.nombre_pais,
        TBL_ESTADOS.nombre_estado,
        TBL_USUARIOS.foto_usuario  # Añadir foto del usuario
    )\
    .join(TBL_SEXOS, TBL_ALUMNOS.idSexo == TBL_SEXOS.id_sexos)\
    .join(TBL_CLINICAS, TBL_ALUMNOS.idClinica == TBL_CLINICAS.id_clinicas)\
    .join(TBL_CARRERAS_TECNICAS, TBL_ALUMNOS.idCarreraTecnica == TBL_CARRERAS_TECNICAS.id_carrera_tecnica)\
    .join(TBL_GRADOS, TBL_ALUMNOS.idGrado == TBL_GRADOS.id_grado)\
    .join(TBL_GRUPOS, TBL_ALUMNOS.idGrupo == TBL_GRUPOS.id_grupos)\
    .join(TBL_PAISES, TBL_ALUMNOS.idPais == TBL_PAISES.id_pais)\
    .join(TBL_ESTADOS, TBL_ALUMNOS.idEstado == TBL_ESTADOS.id_estado)\
    .join(TBL_USUARIOS, TBL_ALUMNOS.idUsuario == TBL_USUARIOS.id_usuario)\
    .filter(TBL_ALUMNOS.idUsuario == id_usuario).first()
        
    if not alumno:
        return jsonify({'error': 'Alumno no encontrado'}), 404
    
    alumno_data = alumno[0]  # Datos del alumno
    nombre_sexo = alumno[1]  # Nombre del sexo
    nombre_clinica = alumno[2]  # Nombre de la clínica
    nombre_carrera_tecnica = alumno[3]  # Nombre de la carrera técnica
    foto_carrera_tecnica = alumno[4]  # Foto de la carrera técnica
    nombre_grado = alumno[5]  # Nombre del grado
    nombre_grupo = alumno[6]  # Nombre del grupo
    nombre_pais = alumno[7]  # Nombre del país
    nombre_estado = alumno[8]  # Nombre del estado
    foto_usuario = alumno[9]  # Foto del usuario

    return jsonify({
        'id_alumnos': alumno_data.id_alumnos,
        'nombre_alumnos': alumno_data.nombre_alumnos,
        'app_alumnos': alumno_data.app_alumnos,
        'apm_alumnos': alumno_data.apm_alumnos,
        'foto_alumnos': b64encode(foto_usuario).decode('utf-8') if foto_usuario else None,
        'fecha_nacimiento_alumnos': alumno_data.fecha_nacimiento_alumnos,
        'curp_alumnos': alumno_data.curp_alumnos,
        'nocontrol_alumnos': alumno_data.nocontrol_alumnos,
        'telefono_alumnos': alumno_data.telefono_alumnos,
        'seguro_social_alumnos': alumno_data.seguro_social_alumnos,
        'cuentacredencial_alumnos': alumno_data.cuentacredencial_alumnos,
        'sexo': nombre_sexo,  # Incluye el nombre del sexo en la respuesta
        'clinica': nombre_clinica,  # Incluye el nombre de la clínica en la respuesta
        'carrera_tecnica': nombre_carrera_tecnica,  # Incluye el nombre de la carrera técnica en la respuesta
        'foto_carrera_tecnica': b64encode(foto_carrera_tecnica).decode('utf-8') if foto_carrera_tecnica else None,  # Foto de la carrera técnica
        'grado': nombre_grado,  # Incluye el nombre del grado en la respuesta
        'grupo': nombre_grupo,  # Incluye el nombre del grupo en la respuesta
        'pais': nombre_pais,  # Incluye el nombre del país en la respuesta
        'estado': nombre_estado,  # Incluye el nombre del estado en la respuesta
        'idUsuario': alumno_data.idUsuario,
        'idTraslado': alumno_data.idTraslado,
        'idTrasladotransporte': alumno_data.idTrasladotransporte,
        'municipio_alumnos': alumno_data.municipio_alumnos,
        'comunidad_alumnos': alumno_data.comunidad_alumnos,
        'calle_alumnos': alumno_data.calle_alumnos,
        'proc_sec_alumno': alumno_data.proc_sec_alumno
    }), 200
