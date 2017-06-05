# Configuration

import sys
from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref

from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    # item = relationship("Item", cascade="all,delete")


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_name = Column(String, ForeignKey('category.name',
                                              ondelete='CASCADE'))
    category = relationship(Category,
                            backref=backref("item", passive_deletes=True))

# End of file
engine = create_engine("sqlite:///categories.db")

Base.metadata.create_all(engine)
