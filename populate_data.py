from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, Category, Item, User

engine = create_engine('postgresql://catalog:superman1$@localhost/catalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()

session = DBSession()

# Users

User1 = User(name="Niraj Pandkar", email="niraj.pandkar@gmail.com",
             picture='https://lh3.googleusercontent.com/-M6uS4os3Rtc/'
                     'AAAAAAAAAAI/AAAAAAAAANM/nRgyFkTWNuI/photo.jpg')
session.add(User1)
session.commit()

# Items in Science Fiction

Genre1 = Category(name="Fiction",
                  user_id=1)

session.add(Genre1)
session.commit()

Book1 = Item(name="The Fault in Our Stars",
             user_id=1,
             description="Despite the tumor-shrinking medical miracle that has "
                         "bought her a few years, Hazel has never been "
                         "anything but terminal, her final chapter inscribed "
                         "upon diagnosis. But when a gorgeous plot twist "
                         "named Augustus Waters suddenly appears at Cancer "
                         "Kid Support Group, Hazel's story is about to be "
                         "completely rewritten.",
             category=Genre1)

session.add(Book1)
session.commit()

Book2 = Item(name="All the Light We Cannot See",
             user_id=1,
             description="From the highly acclaimed, multiple award-winning "
                         "Anthony Doerr, the beautiful, stunningly ambitious "
                         "instant New York Times bestseller about a blind "
                         "French girl and a German boy whose paths collide "
                         "in occupied France as both try to survive the "
                         "devastation of World War II.",
             category=Genre1)

session.add(Book2)
session.commit()

# Items in Mystery

Genre2 = Category(name="Mystery",
                  user_id=1)

session.add(Genre2)
session.commit()

Book1 = Item(name="Missing Melissa",
             user_id=1,
             description="This is the story of Melissa. While Madeline and "
                         "Melissa were going for a doctor's appointment"
                         "their car was hijacked.",
             category=Genre2)

session.add(Book1)
session.commit()

