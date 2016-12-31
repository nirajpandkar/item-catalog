# Configuration

import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_name = Column(String, ForeignKey('category.name'))
    category = relationship(Category)

# End of file
engine = create_engine("sqlite:///categories.db")

Base.metadata.create_all(engine)
