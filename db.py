from sqlalchemy import create_engine
import settings


engine = create_engine(settings.DB_URL, echo=True)
