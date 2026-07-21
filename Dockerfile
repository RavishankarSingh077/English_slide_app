# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim

# Copy local code to the container image.
WORKDIR /app
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Create a user with ID 1000 (required by Hugging Face Spaces)
RUN useradd -m -u 1000 user
RUN chown -R user:user /app
USER user

# Set environment variables
ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Expose the port Hugging Face expects
EXPOSE 7860

# Run the web service on container startup.
# Gunicorn binds to 0.0.0.0:7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
