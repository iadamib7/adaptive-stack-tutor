from backend.app.database.connection import Base, engine


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)