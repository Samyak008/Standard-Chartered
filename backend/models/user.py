from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    dob = Column(Date, nullable=False)
    income = Column(Integer, nullable=False)
    employment_type = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(name={self.name}, dob={self.dob}, income={self.income}, employment_type={self.employment_type})>"