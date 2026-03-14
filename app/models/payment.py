from sqlalchemy import Column, Integer, Text, Float
from app.models.base import Base


class Payment(Base):
    __tablename__ = "payments"

    payment_id  = Column(Text, primary_key=True)
    telegram_id = Column(Text, nullable=False, index=True)
    plano_id    = Column(Text)
    quantidade  = Column(Integer)
    valor       = Column(Float)
    cpf         = Column(Text)
    status      = Column(Text, default="pending")
    criado_em   = Column(Integer, nullable=False)
