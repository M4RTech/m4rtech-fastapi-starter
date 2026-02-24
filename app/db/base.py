from sqlalchemy.orm import DeclarativeBase
from app.db import models # noqa f401

class Base(DeclarativeBase):
    pass

