from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import redis

app = FastAPI()


db = redis.Redis(host='localhost', port=6379, decode_responses=True)


templates = Jinja2Templates(directory="templates")


CAPITULOS = [
    {"id": 1, "nombre": "Cap. 1: El mandaloriano", "temp": 1}, {"id": 2, "nombre": "Cap. 2: El niño", "temp": 1},
    {"id": 3, "nombre": "Cap. 3: El pecado", "temp": 1}, {"id": 4, "nombre": "Cap. 4: Santuario", "temp": 1},
    {"id": 5, "nombre": "Cap. 5: El pistolero", "temp": 1}, {"id": 6, "nombre": "Cap. 6: El prisionero", "temp": 1},
    {"id": 7, "nombre": "Cap. 7: El ajuste de cuentas", "temp": 1}, {"id": 8, "nombre": "Cap. 8: Redención", "temp": 1},
    {"id": 9, "nombre": "Cap. 9: El mariscal", "temp": 2}, {"id": 10, "nombre": "Cap. 10: La pasajera", "temp": 2},
    {"id": 11, "nombre": "Cap. 11: La heredera", "temp": 2}, {"id": 12, "nombre": "Cap. 12: El asedio", "temp": 2},
    {"id": 13, "nombre": "Cap. 13: La Jedi", "temp": 2}, {"id": 14, "nombre": "Cap. 14: La tragedia", "temp": 2},
    {"id": 15, "nombre": "Cap. 15: El creyente", "temp": 2}, {"id": 16, "nombre": "Cap. 16: El rescate", "temp": 2},
    {"id": 17, "nombre": "Cap. 17: El apóstata", "temp": 3}, {"id": 18, "nombre": "Cap. 18: Las minas de Mandalore", "temp": 3},
    {"id": 19, "nombre": "Cap. 19: El converso", "temp": 3}, {"id": 20, "nombre": "Cap. 20: El huérfano", "temp": 3},
    {"id": 21, "nombre": "Cap. 21: El pirata", "temp": 3}, {"id": 22, "nombre": "Cap. 22: Pistoleros a sueldo", "temp": 3},
    {"id": 23, "nombre": "Cap. 23: Los espías", "temp": 3}, {"id": 24, "nombre": "Cap. 24: El regreso", "temp": 3},
]


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/capitulos")
def api_listar():
    res = []
    for c in CAPITULOS:
        
        if db.exists(f"alquiler:{c['id']}"): 
            est = "Alquilado"
        elif db.exists(f"reserva:{c['id']}"): 
            est = "Reservado"
        else: 
            est = "Disponible"
        
        
        res.append({
            "id": c["id"], 
            "nombre": c["nombre"], 
            "estado": est
        })
    return res


@app.post("/api/reservar/{id_cap}")
def api_reservar(id_cap: int):
    if db.exists(f"alquiler:{id_cap}") or db.exists(f"reserva:{id_cap}"):
        raise HTTPException(status_code=400, detail="No disponible")
    
    db.setex(f"reserva:{id_cap}", 240, "espera")
    return {"status": "ok"}


@app.post("/api/confirmar/{id_cap}")
def api_confirmar(id_cap: int, precio: float = 500.0):
    if not db.exists(f"reserva:{id_cap}"):
        raise HTTPException(status_code=400, detail="Sin reserva")
    
    db.setex(f"alquiler:{id_cap}", 86400, str(precio))
    db.delete(f"reserva:{id_cap}")
    return {"status": "ok"}