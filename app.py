from sqlmodel import SQLModel
from db import engine


def build_all():
    from orm import models  # need to import for create_all
    SQLModel.metadata.create_all(engine)


if __name__ == '__main__':
    build_all()
