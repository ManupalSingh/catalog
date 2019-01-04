from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Manufacturer(Base):
        __tablename__ = 'manufacturer'

        id = Column(Integer, primary_key=True)
        name = Column(String(250), nullable=False)
        user_id = Column(Integer, ForeignKey('user.id'))
        user = relationship(User)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
                    'name': self.name,
                    'id': self.id,
             }


class Candy(Base):
        __tablename__ = 'candy'

        name = Column(String(80), nullable=False)
        id = Column(Integer, primary_key=True)
        description = Column(String(250))
        price = Column(String(8))
        manufacturedat = Column(String(250))
        manufacturer_id = Column(Integer, ForeignKey('manufacturer.id'))
        manufacturer = relationship(Manufacturer)
        user_id = Column(Integer, ForeignKey('user.id'))
        user = relationship(User)

        @property
        def serialize(self):
            """Return object data in easily serializeable format"""
            return {
                    'name': self.name,
                    'description': self.description,
                    'id': self.id,
                    'price': self.price,
                    'manufacturedat': self.manufacturedat,
            }

engine = create_engine('sqlite:///candymanufacturers.db')


Base.metadata.create_all(engine)
