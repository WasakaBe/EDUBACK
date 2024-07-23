from flask import Blueprint, jsonify, request
from Database.Database import db, TBL_HORARIO_ALUMNOS, TBL_ALUMNOS
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

horario_alumnos_bp = Blueprint('horario_alumnos_bp', __name__)

