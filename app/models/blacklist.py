from sqlalchemy import Column, Integer, Text
from app.models.base import Base


class Blacklist(Base):
    __tablename__ = "blacklist"

    telegram_id = Column(Text, primary_key=True)
    motivo      = Column(Text)
    criado_em   = Column(Integer, nullable=False)
