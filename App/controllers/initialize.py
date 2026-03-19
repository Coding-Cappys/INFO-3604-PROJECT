from tkinter.font import names

from .user import create_user
from App.database import db


def initialize():
    db.drop_all()
    db.create_all()
    create_user('bob', 'bobpass')
    names = [
    "Alice", "Rob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ian", "Jack",
    "Karen", "Leo", "Mia", "Nina", "Oscar", "Paula", "Quentin", "Rachel", "Steve", "Tina",
    "Uma", "Victor", "Wendy", "Xander", "Yara", "Zane", "Liam", "Sophia", "Noah", "Olivia"
    ]

    for name in names:
        password = name.lower() + "pass"  # simple password scheme, e.g., bobpass
        create_user(name, password)