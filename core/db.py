# core/db.py
from typing import Optional, Generator
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from core.utils.logger import get_logger

logger = get_logger('database')


class Database:

    def __init__(self, pipeline_name: str, connection_url: str):
        self.pipeline_name = pipeline_name
        self.connection_url = connection_url
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._is_connected = False
    
    def connect(self) -> None:
        """Connect to database."""
        if self._is_connected:
            logger.warning(f"⚠️ [{self.pipeline_name}] Base de datos ya está conectada")
            return
        
        try:
            self._engine = create_engine(
                self.connection_url,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Verify connection
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create session factory
            self._session_factory = sessionmaker(bind=self._engine, expire_on_commit=False)
            
            self._is_connected = True
            logger.info(f"🔌 [{self.pipeline_name}] Base de datos conectada")
            
        except Exception as e:
            logger.error(f"❌ [{self.pipeline_name}] Error al conectar: {str(e)}")
            raise
    
    def disconnect(self) -> None:
        if not self._is_connected:
            return
        
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
            
            self._is_connected = False
            logger.info(f"🔌 [{self.pipeline_name}] Base de datos desconectada")
            
        except Exception as e:
            logger.error(f"❌ [{self.pipeline_name}] Error al desconectar: {str(e)}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get a SQLAlchemy session for ORM operations."""
        if not self._is_connected:
            raise RuntimeError(f"[{self.pipeline_name}] Not connected. Call connect() first.")
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"❌ [{self.pipeline_name}] Error en sesión: {str(e)}")
            raise
        finally:
            session.close()
    
    @contextmanager
    def get_connection(self):
        """Get a raw database connection for non-ORM operations."""
        if not self._is_connected:
            raise RuntimeError(f"[{self.pipeline_name}] Not connected. Call connect() first.")
        
        connection = self._engine.raw_connection()
        try:
            yield connection
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"❌ [{self.pipeline_name}] Error en conexión: {str(e)}")
            raise
        finally:
            connection.close()
    
    @property
    def engine(self) -> Engine:
        if not self._is_connected:
            raise RuntimeError(f"[{self.pipeline_name}] Not connected. Call connect() first.")
        return self._engine
    
    @property
    def is_connected(self) -> bool:
        return self._is_connected
    
    
# Example usage:
'''
from core.db import Database

# 1. Crear instancia y conectar
db = Database("mi_pipeline", "postgresql://user:password@localhost:5432/mydatabase")
db.connect()

# 2. Usar con ORM (Session)
with db.get_session() as session:
    # Hacer queries con SQLAlchemy ORM
    users = session.query(User).filter(User.active == True).all()
    
    # Crear datos
    new_user = User(name="Juan", email="juan@example.com")
    session.add(new_user)
    # Commit automático al salir del contexto

# 3. Usar raw SQL
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE active = true")
    rows = cursor.fetchall()
    # Commit automático al salir

# 4. Acceso al engine (si lo necesitas)
if db.is_connected:
    engine = db.engine
    # ... usar engine directamente

# 5. Desconectar
db.disconnect()
'''