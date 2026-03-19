from datetime import date, time
from tkinter.font import names

from .user import create_user
from .event import create_event
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
        password = name.lower() + "pass"  
        create_user(name, password)
        
    create_event(
    "Opening Ceremony",
    date(2026, 4, 1),
    time(9, 0),
    "Main Hall",
    "ceremony"
    )

    create_event(
        "AI in Healthcare",
        date(2026, 4, 1),
        time(10, 0),
        "Room A",
        "presentation"
    )

    create_event(
        "Cybersecurity Trends",
        date(2026, 4, 1),
        time(11, 30),
        "Room B",
        "presentation"
    )

    create_event(
        "Lunch Break",
        date(2026, 4, 1),
        time(13, 0),
        "Cafeteria",
        "break"
    )

    create_event(
        "Machine Learning Workshop",
        date(2026, 4, 1),
        time(14, 0),
        "Lab 1",
        "presentation"
    )

    create_event(
        "Closing Ceremony",
        date(2026, 4, 1),
        time(17, 0),
        "Main Hall",
        "ceremony"
    )