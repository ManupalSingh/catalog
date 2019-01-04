from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Manufacturer, Base, Candy, User

engine = create_engine('sqlite:///candymanufacturers.db',
                       connect_args={'check_same_thread': False})

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

User1 = User(name="Manupal Singh", email="manupalsingh3@gmail.com")
session.add(User1)
session.commit()

manufacturer1 = Manufacturer(user_id=1, name="Cadbury")

session.add(manufacturer1)
session.commit()

candy1 = Candy(user_id=1,
               name="Dairy Milk",
               description="classic milk chocolate for all ocassions",
               price="$2.99", manufacturedat="New York",
               manufacturer=manufacturer1)

session.add(candy1)
session.commit()

candy2 = Candy(user_id=1, name="Creme Egg",
               description="the wonder egg",
               price="$5.50", manufacturedat="Seattle",
               manufacturer=manufacturer1)

session.add(candy2)
session.commit()

candy3 = Candy(user_id=1, name="Buttons",
               description="Happiness in small size",
               price="$3.99", manufacturedat="Chicago",
               manufacturer=manufacturer1)

session.add(candy3)
session.commit()

manufacturer2 = Manufacturer(user_id=1, name="Nestle")

session.add(manufacturer2)
session.commit()

candy4 = Candy(user_id=1, name="Aero",
               description="modern chocolate for the modern world",
               price="$3.25", manufacturedat="San Francisco",
               manufacturer=manufacturer2)

session.add(candy4)
session.commit()

candy5 = Candy(user_id=1, name="Butterfinger",
               description="smooth as butter",
               price="$2.50", manufacturedat="Austin",
               manufacturer=manufacturer2)

session.add(candy5)
session.commit()

candy6 = Candy(user_id=1, name="Crunch",
               description="Contains crunchy dry fruit",
               price="$2.99", manufacturedat="Miami",
               manufacturer=manufacturer2)

session.add(candy6)
session.commit()

print ("added candies!")
