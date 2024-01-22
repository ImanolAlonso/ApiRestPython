from sqlalchemy import String, Integer, Column, BLOB, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Producto(Base):
    __tablename__ = 'Producto'
    id = Column(Integer, primary_key=True, index=True)
    nombreProducto = Column(String)
    stock = Column(Integer)
    fecha = Column(Date)
    nombreImagen = Column(String)
    imagen = Column(BLOB)
    idCategoria = Column(Integer, ForeignKey('Categoria.idCategoria'))
    categoria = relationship('Categoria', back_populates='productos')

class Categoria(Base):
    __tablename__ = 'Categoria'
    idCategoria = Column(Integer, primary_key=True, index=True)
    nombreCategoria = Column(String)
    productos = relationship('Producto', back_populates='categoria')