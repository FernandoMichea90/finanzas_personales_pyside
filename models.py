from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from config import DATABASE_URL
import os
import hashlib

# Eliminar la base de datos existente si existe
if os.path.exists("finanzas.db"):
    os.remove("finanzas.db")

Base = declarative_base()
engine = create_engine(DATABASE_URL)

class Usuario(Base):
    __tablename__ = 'usuarios'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    apellido = Column(String)
    email = Column(String, unique=True)
    rut = Column(String, unique=True)
    telefono = Column(String)
    fecha_nacimiento = Column(DateTime)
    transacciones = relationship("Transaccion", back_populates="usuario")
    credencial = relationship("Credencial", back_populates="usuario", uselist=False)
    categorias = relationship("Categoria", back_populates="usuario")

class Credencial(Base):
    __tablename__ = 'credenciales'
    
    id = Column(Integer, primary_key=True)
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    email = Column(String, unique=True)
    password_hash = Column(String)
    usuario = relationship("Usuario", back_populates="credencial")

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    def verificar_password(self, password):
        return self.password_hash == self.hash_password(password)

class Categoria(Base):
    __tablename__ = 'categorias'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    tipo = Column(String)  # 'Ingreso' o 'Gasto'
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    usuario = relationship("Usuario", back_populates="categorias")
    transacciones = relationship("Transaccion", back_populates="categoria")

class Transaccion(Base):
    __tablename__ = 'transacciones'
    
    id = Column(Integer, primary_key=True)
    fecha = Column(DateTime, default=datetime.now)
    descripcion = Column(String)
    monto = Column(Float)
    tipo = Column(String)  # 'Ingreso' o 'Gasto'
    usuario_id = Column(Integer, ForeignKey('usuarios.id'))
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    usuario = relationship("Usuario", back_populates="transacciones")
    categoria = relationship("Categoria", back_populates="transacciones")

# Crear las tablas
Base.metadata.create_all(engine) 