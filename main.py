import os
import sys
import uvicorn

print("=== Initializing Master English AI Tutor ===", flush=True)

try:
    from app import app
    print("=== Successfully loaded FastAPI app ===", flush=True)
except Exception as e:
    print(f"CRITICAL ERROR importing app: {e}", file=sys.stderr, flush=True)
    sys.exit(1)

if __name__ == "__main__":
    raw_port = os.getenv("PORT", "7860").strip()
    try:
        port = int(raw_port)
    except Exception as err:
        print(f"Warning: Invalid PORT '{raw_port}', defaulting to 7860. Error: {err}", flush=True)
        port = 7860

    print(f"=== Launching Uvicorn Server on 0.0.0.0:{port} ===", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
