import os

from fastapi.templating import Jinja2Templates

from ..database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory=os.path.join(os.path.abspath(os.path.dirname(__file__)), os.path.join("templates")))
