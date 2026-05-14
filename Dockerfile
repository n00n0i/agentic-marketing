# Stage 1: Python backend
FROM python:3.12-slim AS backend

WORKDIR /app

# Install dependencies
COPY pyproject.toml .env.example ./
RUN pip install --no-cache-dir --prefix=/install -e ".[server]"

# Copy source
COPY src/ src/
COPY schemas/ schemas/
COPY skills/ skills/
COPY pipeline_defs/ pipeline_defs/

# Runtime deps only (no build tools)
RUN pip install --no-cache-dir --prefix=/install uvicorn[standard]

# ── Stage 2: Node frontend build ──────────────────────────────────────────
FROM node:22-alpine AS frontend-build

WORKDIR /app
COPY frontend/package*.json frontend/
RUN npm ci --quiet

COPY frontend/ ./
RUN npm run build

# ── Stage 3: Production nginx ─────────────────────────────────────────────
FROM nginx:1.27-alpine AS production

# Nginx config — spa + proxy to backend
COPY <<'EOF' /etc/nginx/conf.d/default.conf
server {
    listen 80;
    server_name _;

    # Next.js static files
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend:8000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
EOF

# Copy Next.js build output
COPY --from=frontend-build /app/.next /usr/share/nginx/html/.next
COPY --from=frontend-build /app/public /usr/share/nginx/html/public

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]