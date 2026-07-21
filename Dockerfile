FROM python:3.9-slim
WORKDIR /app
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
CMD gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT:-7860} app:app
