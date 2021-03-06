# -*- coding: utf-8 -*-
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

    @property
    def serialize(self):
        # Returns users in easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture_url': self.picture
        }


class Category(Base):
    __tablename__ = 'category'
    name = Column(String(80), nullable=False, unique=True)
    id = Column(Integer, primary_key=True)
    items = relationship("Item", cascade="all,delete-orphan")
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


class Item(Base):
    __tablename__ = 'item'
    name = Column(String(200), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(2000))

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship(User)

    @property
    def serialize(self):
        # Returns object data in easily serializable format
        return{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category.id,
            'user_id': self.user_id
        }

# End of file
engine = create_engine('postgresql://catalog:superman1$@localhost/catalog')

Base.metadata.create_all(engine)
