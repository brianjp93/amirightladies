from sqlmodel import SQLModel
from orm import models
import settings
from db import engine


def build_all():
    SQLModel.metadata.create_all(engine)
