from sqlalchemy import Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base

RepdBase = declarative_base()

class Sexos(RepdBase):
    __tablename__ = 'sexos'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)

class Nacionalidades(RepdBase):
    __tablename__ = 'nacionalidades'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class RangosEdades(RepdBase):
    __tablename__ = 'rangos_edades'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)

class Estados(RepdBase):
    __tablename__ = 'estados'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class Municipios(RepdBase):
    __tablename__ = 'municipios'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class EstatusDesapariciones(RepdBase):
    __tablename__ = 'estatus_desapariciones'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class CondicionesLocalizaciones(RepdBase):
    __tablename__ = 'condiciones_localizaciones'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class ClasificacionesLocalizaciones(RepdBase):
    __tablename__ = 'clasificaciones_localizaciones'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class TiposCierres(RepdBase):
    __tablename__ = 'tipos_cierres'
    
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(100), nullable=False)

class Desaparecidos(RepdBase):
    __tablename__ = 'desaparecidos'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    folio_estatal_busqueda = Column(String(100), nullable=False)
    sexo_id = Column(Integer, ForeignKey('sexos.id'), nullable=False)
    nacionalidad_id = Column(Integer, ForeignKey('nacionalidades.id'), nullable=False)
    rango_edad_id = Column(Integer, ForeignKey('rangos_edades.id'), nullable=False)
    fecha_reporte = Column(Date, nullable=False)
    fecha_desaparicion = Column(Date, nullable=True)
    estado_desaparicion_id = Column(Integer, ForeignKey('estados.id'), nullable=False)
    municipio_desaparicion_id = Column(Integer, ForeignKey('municipios.id'), nullable=False)
    estatus_desaparicion_id = Column(Integer, ForeignKey('estatus_desapariciones.id'), nullable=False)
    fecha_localizacion = Column(Date, nullable=True)
    condicion_localizacion_id = Column(Integer, ForeignKey('condiciones_localizaciones.id'), nullable=True)
    clasificacion_localizacion_id = Column(Integer, ForeignKey('clasificaciones_localizaciones.id'), nullable=True)
    estado_localizacion_id = Column(Integer, ForeignKey('estados.id'), nullable=True)
    municipio_localizacion_id = Column(Integer, ForeignKey('municipios.id'), nullable=True)
    fecha_cierre = Column(Date, nullable=True)
    tipo_cierre_id = Column(Integer, ForeignKey('tipos_cierres.id'), nullable=True)
    folio_estatal_busqueda_vinculado = Column(String(100), nullable=True)
    carpeta_investigacion = Column(Boolean, nullable=True)