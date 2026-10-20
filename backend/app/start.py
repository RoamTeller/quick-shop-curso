import subprocess
import uvicorn
from .seed import seed

if __name__ == "__main__":
    subprocess.run(["uv", "run", "--frozen", "alembic", "upgrade", "head"], check=True)
    seed()
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
