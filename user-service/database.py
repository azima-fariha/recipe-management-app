import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from models import Base

load_dotenv()  # Load environment variables from .env file

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL, echo=True, future=True)

# Create all tables on startup
# this is happening for ORM. It will create the tables in the 
# database based on the models defined in the models.py file.
Base.metadata.create_all(bind=engine) 

# calling SessionLocal() gives you one DB session (a unit-of-work 
# tracks changes, lets you commit/rollback)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# get_db() is a generator-based FastAPI dependency: it hands a session
# to a route via Depends(get_db), and the finally guarantees the session closes after the request, even if the route raises an error.
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
