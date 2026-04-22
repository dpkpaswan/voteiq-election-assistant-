"""
Application entry point for VoteIQ — Election Process Education Assistant
"""

import uvicorn
import logging

from .server import create_app
from .config import config

# -----------------------------
# 🧾 LOGGING SETUP
# -----------------------------
logging.basicConfig(
    level=config.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

# -----------------------------
# 🚀 CREATE APP
# -----------------------------
app = create_app()


# -----------------------------
# ▶️ RUN SERVER
# -----------------------------
def run():
    """Run FastAPI server using config settings"""

    logger.info("Starting VoteIQ server...")
    logger.info(f"Environment: {config.ENV}")
    logger.info(f"Mode: {config.DEFAULT_MODE}")

    uvicorn.run(
        "app.main:app",   # safer import string for reload
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )


# -----------------------------
# 🧪 OPTIONAL: CLI ENTRY
# -----------------------------
if __name__ == "__main__":
    run()