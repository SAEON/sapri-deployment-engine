# database.py

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

# Replace with your actual database connection string
DATABASE_URL = "postgresql://sapri_db_user:password@localhost:5400/sapri_deployment"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Deployment(Base):
    """
    SQLAlchemy ORM model for the 'deployment' table.
    """
    __tablename__ = 'deployment'

    deployment_id = Column(String, primary_key=True, name="deployment_id")
    date_time = Column(Integer, name="date_time")

    def __repr__(self):
        return f"<Deployment(deployment_id='{self.deployment_id}', date_time='{self.date_time}')>"


def get_db():
    """
    Dependency to get a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates the database table if it doesn't exist.
    """
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database table created successfully.")
