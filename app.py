from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from typing import List
from datetime import date
import io
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse


app = FastAPI()

class ActualizarProducto(BaseModel):
    nombreProducto:str
    stock:int
    fecha: date
    categoria: str

class IntroducirProducto(BaseModel):
    nombreProducto: str
    stock: int
    fecha: date
    categoria:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/productos",status_code=status.HTTP_200_OK)
def consultar_productos(db:db_dependency):
    productos = db.query(models.Producto).all()
    productos_sin_imagen = [{"id": producto.id, "nombreProducto": producto.nombreProducto, "stock": producto.stock, "fecha": producto.fecha, "nombreImagen": producto.nombreImagen, "categoria":producto.categoria} for producto in productos]
    return productos_sin_imagen

@app.get("/producto/{id}", status_code=status.HTTP_200_OK)
def consultar_producto(id, db:db_dependency):
    producto = db.query(models.Producto).filter(models.Producto.id==id).first()
    if producto is None:
        HTTPException(status_code=404, detail="Producto no encontrado")
    producto_sin_imagen = {"id": producto.id, "nombreProducto": producto.nombreProducto, "stock": producto.stock, "fecha": producto.fecha, "nombreImagen": producto.nombreImagen,"categoria":producto.categoria}
    return producto_sin_imagen

@app.delete("/producto/{id}", status_code=status.HTTP_200_OK)
def borrar_producto(id, db:db_dependency):
    borrarProducto = db.query(models.Producto).filter(models.Producto.id==id).first()
    if borrarProducto is None:
        HTTPException(status_code=404, detail="No se puede borrar no exite el producto")
    db.delete(borrarProducto)
    db.commit()
    return "EL producto se eliminó correctamente"

@app.post("/producto/")
def crear_producto(producto: IntroducirProducto,db: db_dependency):
    buscar_categoria = db.query(models.Categoria).filter(models.Categoria.nombreCategoria==producto.categoria).first()
    if buscar_categoria is None:
        raise HTTPException(status_code=404, detail="Categoria no válida")
    db_producto = models.Producto(
    nombreProducto=producto.nombreProducto,
    stock=producto.stock,
    fecha=producto.fecha,
    categoria=buscar_categoria,
    nombreImagen = ""
)

    db.add(db_producto)
    db.commit()
    return {"mensaje": "El producto se creó correctamente", "id_producto": db_producto.id}

@app.put("/producto/{id}", status_code=status.HTTP_200_OK)
def actualizar_producto(id, producto: ActualizarProducto, db: db_dependency):
    actualizar_producto = db.query(models.Producto).filter(models.Producto.id == id).first()
    buscar_categoria = db.query(models.Categoria).filter(models.Categoria.nombreCategoria==producto.categoria).first()
    if actualizar_producto is None:
        raise HTTPException(status_code=404, detail="No se encuentra el producto")
    if buscar_categoria is None:
        HTTPException(status_code=404, detail="Categoria no válida")
    # Actualizar campos del producto
    actualizar_producto.nombreProducto = producto.nombreProducto
    actualizar_producto.stock = producto.stock
    actualizar_producto.fecha = producto.fecha
    actualizar_producto.idCategoria = buscar_categoria.idCategoria
    actualizar_producto.categoria = buscar_categoria

    db.commit()
    return "El producto se actualizó correctamente"

#Actualizar imagen de un id concreto
@app.put("/producto/{id}/imagen", status_code=status.HTTP_200_OK)
def actualizar_imagen_producto(id: int, db: Session = Depends(get_db), imagen: UploadFile = File(...)):
    actualizar_producto = db.query(models.Producto).filter(models.Producto.id == id).first()
    
    if not actualizar_producto:
        raise HTTPException(status_code=404, detail="No se encuentra el producto")

    # Actualizar imagen y nombre de imagen si se proporciona una nueva
    max_size_kb = 64
    max_size_bytes = max_size_kb * 1024
    imagen_leida = imagen.file.read()

    if len(imagen_leida) > max_size_bytes:
        raise HTTPException(status_code=422, detail="La imagen excede el tamaño máximo permitido (64 KB)")

    # Guardar la imagen en la base de datos
    actualizar_producto.imagen = imagen_leida
    actualizar_producto.nombreImagen = imagen.filename

    db.commit()

    return "La imagen del producto se actualizó correctamente"

#Mostrar imagen de un id concreto
@app.get("/producto/{id}/imagen/", status_code=status.HTTP_200_OK)
def obtener_imagen_producto(id, db: db_dependency):
    producto = db.query(models.Producto).filter(models.Producto.id == id).first()
    if producto is None or producto.imagen is None:
        raise HTTPException(status_code=404, detail="Producto o imagen no encontrados")
    return StreamingResponse(io.BytesIO(producto.imagen), media_type="image/jpeg")
