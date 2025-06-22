from sqlalchemy import Column, Integer, String
from .model.databese import Base

#Модель пользователя
class UserDB(Base):
    __tablename__ = "colleague"
    id = Column(Integer, primary_key=True,index=True, comment="Уникальный номер ID коллеги")
    first_name = Column(String(80), index=True, nullable=False, comment="Имя коллеги")
    last_name = Column(String(80), index=True, nullable=False, comment="Фамилия коллеги")
    number = Column(String(18), unique=True, index=True, nullable=False, comment="Уникальный номер коллеги")