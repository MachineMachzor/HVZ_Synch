from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#From https://fastapi.tiangolo.com/tutorial/sql-databases/

#JUST CHANGED THE DATABASE NAME HERE
SQLALCHEMY_DATABASE_URL = "sqlite:///./hvz.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

SQLALCHEMY_LOGIN_URL = "sqlite:///./userPass.db"

SQLALCHEMY_MISSIONS_URL = "sqlite:///./missions.db"




engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

engineUserPass = create_engine(
    SQLALCHEMY_LOGIN_URL, connect_args={"check_same_thread": False}
)

engineMissions = create_engine(
    SQLALCHEMY_MISSIONS_URL, connect_args={"check_same_thread": False}
)



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocalUserPass = sessionmaker(autocommit=False, autoflush=False, bind=engineUserPass)
SessionMissions = sessionmaker(autocommit=False, autoflush=False, bind=engineMissions)



Base = declarative_base()