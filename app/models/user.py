from sqlalchemy import Column, Integer, Text
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Text, unique=True, nullable=False)
    username    = Column(Text)
    first_name  = Column(Text)
    created_at  = Column(Integer, nullable=False)
    last_seen   = Column(Integer)
