FROM python:3.11-slim

WORKDIR /app

RUN pip install uv

COPY . /app

# uv = Python ecosystem
# npm/npx = Node.js ecosystem
CMD ["python", "-c", "node", "-v", "print('Docker container is ready')"]