from __future__ import annotations

import uvicorn

from src.api import app
from src.config import AppSettings


if __name__ == "__main__":
    settings = AppSettings()
    uvicorn.run(app, host=settings.api.host, port=settings.api.port, reload=settings.api.reload)
