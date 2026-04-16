from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import redis
import os


app = FastAPI(title="API Turismo - Bases de Datos NoSQL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que cualquier web se conecte
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


redis_host = os.getenv("REDIS_HOST", "redis-db")
redis_port = int(os.getenv("REDIS_PORT", 6379))


r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)


class Lugar(BaseModel):
    nombre: str
    latitud: float
    longitud: float
    grupo: str  

@app.post("/api/lugares", tags=["Lugares"])
def agregar_lugar(lugar: Lugar):
    try:
        
        clave_redis = f"geo:{lugar.grupo.lower()}"
        
        
        r.geoadd(clave_redis, (lugar.longitud, lugar.latitud, lugar.nombre))
        
        return {
            "estado": "éxito",
            "mensaje": f"'{lugar.nombre}' agregado correctamente a '{clave_redis}'"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Redis: {str(e)}")

@app.get("/", tags=["Estado"])
def estado_api():
    return {"mensaje": "API conectada y funcionando"}


@app.get("/api/lugares/cercanos", tags=["Lugares"])
def buscar_cercanos(latitud: float, longitud: float, grupo: str, radio_km: int = 5):
    try:
        clave_redis = f"geo:{grupo.lower()}"
        
        
        resultados = r.geosearch(
            name=clave_redis,
            longitude=longitud,
            latitude=latitud,
            radius=radio_km,
            unit='km',
            withdist=True
        )
        
        
        lugares_formateados = []
        for lugar in resultados:
            lugares_formateados.append({
                "nombre": lugar[0],
                "distancia_km": round(lugar[1], 2) # Redondeamos a 2 decimales
            })
            
        return {
            "estado": "éxito",
            "grupo_buscado": grupo,
            "radio_km": radio_km,
            "resultados": lugares_formateados
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Redis: {str(e)}")
    

@app.get("/api/lugares/distancia", tags=["Lugares"])
def calcular_distancia(latitud: float, longitud: float, grupo: str, nombre_lugar: str):
    try:
        clave_redis = f"geo:{grupo.lower()}"
        
        
        r.geoadd(clave_redis, (longitud, latitud, "UsuarioTemp"))
        
        
        distancia = r.geodist(clave_redis, "UsuarioTemp", nombre_lugar, unit='km')
        
        
        r.zrem(clave_redis, "UsuarioTemp")
        
        
        if distancia is None:
            raise HTTPException(status_code=404, detail="No se encontró el lugar indicado en la base de datos")
            
        return {
            "estado": "éxito",
            "origen": "Tu ubicación",
            "destino": nombre_lugar,
            "distancia_km": round(distancia, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en Redis: {str(e)}")    