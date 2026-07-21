FROM python:3.9-slim
WORKDIR /app
COPY . ./
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH
EXPOSE 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
