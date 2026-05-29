from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.api import router as api_router
from app.core.config import settings
import logging
import os

# Configurar logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para predicción de tráfico en la ciudad de Puno"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Sirve la interfaz Single Page Application (SPA) del frontend."""
    static_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html")
    if os.path.exists(static_file):
        try:
            with open(static_file, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
        except Exception as e:
            logging.error(f"Error al leer index.html: {e}")
            return HTMLResponse(content=f"<h1>Error</h1><p>Error leyendo frontend: {e}</p>", status_code=500)
    return HTMLResponse(
        content="<h1>PunoTraffic AI</h1><p>El frontend estático (index.html) no fue encontrado en backend/app/static/index.html.</p>",
        status_code=404
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)