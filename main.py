from app import app, serve_index, generate_scenario, generate_example

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
