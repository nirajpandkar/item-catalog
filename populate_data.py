#!/usr/bin/python
# -*- coding: utf-8 -*-
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
                         "completely rewritten."
                         "Insightful, bold, irreverent, and raw, The Fault in "
                         "Our Stars is award-winning author John Green's most "
                         "ambitious and heartbreaking work yet, brilliantly "
                         "exploring the funny, thrilling, and tragic business "
                         "of being alive and in love.",
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

Book3 = Item(name="Camino Island",
             user_id=1,
             description="Mercer Mann is a young novelist with a severe case of writer’s block who has recently been laid off from her teaching position. She is approached by an elegant, mysterious woman working for an even more mysterious company. A generous offer of money convinces Mercer to go undercover and infiltrate Bruce Cable’s circle of literary friends, ideally getting close enough to him to learn his secrets.",
             category=Genre1)

session.add(Book3)
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

Book2 = Item(name="The Da Vinci Code",
             user_id=1,
             description="While in Paris, Harvard symbologist Robert Langdon is awakened by a phone call in the dead of the night. The elderly curator of the Louvre has been murdered inside the museum, his body covered in baffling symbols. As Langdon and gifted French cryptologist Sophie Neveu sort through the bizarre riddles, they are stunned to discover a trail of clues hidden in the works of Leonardo da Vinci—clues visible for all to see and yet ingeniously disguised by the painter.",
             category=Genre2)

session.add(Book2)
session.commit()

Genre3 = Category(name="Biography",
                  user_id=1)

session.add(Genre3)
session.commit()

Book1 = Item(name="Elon Musk: Inventing the Future",
             user_id=1,
             description="Vance uses Musk’s story to explore one of the pressing questions of our age: can the nation of inventors and creators who led the modern world for a century still compete in an age of fierce global competition? He argues that Musk—one of the most unusual and striking figures in American business history—is a contemporary, visionary amalgam of legendary inventors and industrialists including Thomas Edison, Henry Ford, Howard Hughes, and Steve Jobs. More than any other entrepreneur today, Musk has dedicated his energies and his own vast fortune to inventing a future that is as rich and far-reaching as the visionaries of the golden age of science-fiction fantasy.",
             category=Genre3)

session.add(Book1)
session.commit()

Book2 = Item(name="The Facebook Effect",
             user_id=1,
             description="Veteran technology reporter David Kirkpatrick had the full cooperation of Facebook’s key executives in researching this fascinating history of the company and its impact on our lives. Kirkpatrick tells us how Facebook was created, why it has flourished, and where it is going next. He chronicles its successes and missteps, and gives readers the most complete assessment anywhere of founder and CEO Mark Zuckerberg, the central figure in the company’s remarkable ascent. This is the Facebook story that can be found nowhere else.",
             category=Genre3)

session.add(Book2)
session.commit()
