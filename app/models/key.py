from sqlalchemy import Column, Integer, Text, Boolean
from app.models.base import Base


class Key(Base):
    __tablename__ = "keys"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    key_str         = Column(Text, unique=True, nullable=False)
    descricao       = Column(Text)
    plano_id        = Column(Text)
    telegram_id     = Column(Text, index=True)
    limite_req      = Column(Integer, default=0)
    usos_restantes  = Column(Integer, default=0)
    expira_em       = Column(Integer)
    ativa           = Column(Boolean, default=True)
    criada_em       = Column(Integer, nullable=False)
    ultimo_uso      = Column(Integer)
