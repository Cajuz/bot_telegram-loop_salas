from sqlalchemy import Column, Integer, Text
from app.models.base import Base


class RoomLog(Base):
    __tablename__ = "rooms_log"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Text, nullable=False, index=True)
    room_id     = Column(Text, nullable=False)
    sshash      = Column(Text)
    modo        = Column(Integer)
    key_str     = Column(Text)
    criado_em   = Column(Integer, nullable=False, index=True)
