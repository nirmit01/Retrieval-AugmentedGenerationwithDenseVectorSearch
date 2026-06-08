version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - HUGGINGFACEHUB_API_TOKEN=${HUGGINGFACEHUB_API_TOKEN}
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    depends_on:
      - backend
    # Use production backend URL
    environment:
      - VITE_API_URL=http://localhost:8000
    restart: unless-stopped