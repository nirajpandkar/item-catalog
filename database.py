# Configuration

import sys
from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship, backref

from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    id = Column(Integer, primary_key=True)


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), primary_key=True, nullable=False)
    id = Column(Integer)
    items = relationship("Item", cascade="all,delete-orphan")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'name': self.name,
            'id': self.id,
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(1000))

    category_name = Column(String, ForeignKey('category.name'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return{
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'category_name': self.category_name
        }

# End of file
engine = create_engine('postgresql://catalog:superman1$@localhost/catalog')

Base.metadata.create_all(engine)