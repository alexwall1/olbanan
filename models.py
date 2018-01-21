from sqlalchemy import Column, String, Integer
from database import Base

class Bar(Base):
	__tablename__ = 'bar'
	id = Column(Integer, primary_key=True)
	eniro_id = Column(Integer, nullable=False)
	vote = Column(Integer, nullable=False)
	name = Column(String(255), nullable=False)
	facebook = Column(String(255), nullable=True)
	homepage = Column(String(255), nullable=True)
	company_reviews = Column(String(255), nullable=True)
	station = Column(String(255), nullable=False)
	zone = Column(Integer, nullable=False)
