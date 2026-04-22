# -----------------------------
# 🐍 BASE IMAGE
# -----------------------------
FROM python:3.11-slim

# -----------------------------
# 📁 WORKDIR
# -----------------------------
WORKDIR /app

# -----------------------------
# ⚙️ ENV SETTINGS
# -----------------------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# 📦 INSTALL DEPENDENCIES
# -----------------------------
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 📂 COPY PROJECT
# -----------------------------
COPY . .

# -----------------------------
# 🔐 NON-ROOT USER (SECURITY)
# -----------------------------
RUN useradd -m appuser
USER appuser

# -----------------------------
# 🌐 PORT
# -----------------------------
EXPOSE 8080

# -----------------------------
# 🚀 START VOTEIQ SERVER
# -----------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]