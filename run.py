from main import app
from src.core.config import settings

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=5001,
        reload=settings.debug,
    )
    