import os
import uvicorn
from app import app

if __name__ == "__main__":
    port_env = os.getenv("PORT", "7860").strip()
    try:
        port = int(port_env)
    except ValueError:
        port = 7860
    print(f"Starting Master English AI server on 0.0.0.0:{port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
