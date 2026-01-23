from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from core.pipelines.datamexico.attributes import DataMexicoTables
DataMexicoBase = declarative_base()

class Paises(DataMexicoBase):
    __tablename__ = DataMexicoTables.PAISES

    pais_id = Column(Integer, primary_key=True, autoincrement=True)
    codigo_pais = Column(String(3), nullable=False, unique=True)
    nombre_pais = Column(String, nullable=False)

class EntidadesFederativas(DataMexicoBase):
    __tablename__ = DataMexicoTables.ENTIDADES_FEDERATIVAS

    entidad_id = Column(Integer, primary_key=True)
    nombre_entidad = Column(String, nullable=False)

class Tiempo(DataMexicoBase):
    __tablename__ = DataMexicoTables.TIEMPOS

    periodo_id = Column(Integer, primary_key=True)
    anio = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    etiqueta_trimestre = Column(String(7), nullable=False)

class TipoFlujoComercial(DataMexicoBase):
    __tablename__ = DataMexicoTables.TIPOS_FLUJOS_COMERCIALES

    tipo_flujo_id = Column(Integer, primary_key=True)
    flujo = Column(String, nullable=False)

class Productos(DataMexicoBase):
    __tablename__ = DataMexicoTables.PRODUCTOS

    producto_id = Column(Integer, primary_key=True)
    descripcion = Column(String, nullable=False)

class FlujoComercio(DataMexicoBase):
    __tablename__ = DataMexicoTables.FLUJO_COMERCIO

    flujo_id = Column(Integer, primary_key=True)
    pais_id = Column(Integer, ForeignKey('paises.pais_id'), nullable=False)
    entidad_id = Column(Integer, ForeignKey('entidades_federativas.entidad_id'), nullable=False)
    periodo_id = Column(Integer, ForeignKey('tiempos.periodo_id'), nullable=False)
    tipo_flujo_id = Column(Integer, ForeignKey('tipos_flujos_comerciales.tipo_flujo_id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('productos.producto_id'), nullable=False)
    valor_comercio = Column(Float, nullable=False)
