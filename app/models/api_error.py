from sqlalchemy import Column, Integer, Text
from app.models.base import Base


class ApiError(Base):
    __tablename__ = "api_errors"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Text)
    endpoint    = Column(Text)
    motivo      = Column(Text)
    criado_em   = Column(Integer, nullable=False)
