from fastapi import FastAPI
from backend.api import router as api_router
import uvicorn
import logging
from datetime import datetime
import os

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/safespace.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("SAFESPACE_API")

app = FastAPI(
    title="SAFESPACE AI AGENT API",
    description="Multimodal Mental Health AI Assistant API",
    version="1.0.0"
)

app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("SAFESPACE AI AGENT API starting up...")
    logger.info(f"Startup time: {datetime.now()}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("SAFESPACE AI AGENT API shutting down...")
    logger.info(f"Shutdown time: {datetime.now()}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)