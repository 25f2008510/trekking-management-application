from app import app
from models import db, Trek
from datetime import date, timedelta
import random

treks_data = [
    ("Kashmir Great Lakes", "Jammu & Kashmir", "Hard", 8, 4300),
    ("Kedarkantha", "Uttarakhand", "Easy", 6, 3810),
    ("Valley of Flowers", "Uttarakhand", "Moderate", 6, 4328),
    ("Hampta Pass", "Himachal Pradesh", "Moderate", 5, 4270),
    ("Rupin Pass", "Uttarakhand", "Hard", 8, 4650),
    ("Goechala", "Sikkim", "Hard", 11, 4940),
    ("Markha Valley", "Ladakh", "Hard", 8, 5200),
    ("Chadar Trek", "Ladakh", "Hard", 9, 3400),
    ("Kuari Pass", "Uttarakhand", "Moderate", 6, 3820),
    ("Brahmatal", "Uttarakhand", "Easy", 6, 3750),
    ("Dayara Bugyal", "Uttarakhand", "Easy", 5, 3650),
    ("Har Ki Dun", "Uttarakhand", "Moderate", 7, 3566),
    ("Sandakphu", "West Bengal", "Moderate", 7, 3636),
    ("Nag Tibba", "Uttarakhand", "Easy", 2, 3022),
    ("Triund", "Himachal Pradesh", "Easy", 2, 2850),
    ("Beas Kund", "Himachal Pradesh", "Easy", 3, 3700),
    ("Bhrigu Lake", "Himachal Pradesh", "Moderate", 4, 4300),
    ("Chandrakhani Pass", "Himachal Pradesh", "Moderate", 5, 3660),
    ("Pin Parvati Pass", "Himachal Pradesh", "Hard", 11, 5319),
    ("Buran Ghati", "Himachal Pradesh", "Hard", 7, 4575),
    ("Sar Pass", "Himachal Pradesh", "Moderate", 5, 4220),
    ("Indrahar Pass", "Himachal Pradesh", "Moderate", 5, 4342),
    ("Kheerganga", "Himachal Pradesh", "Easy", 2, 2960),
    ("Prashar Lake", "Himachal Pradesh", "Easy", 2, 2730),
    ("Tarsar Marsar", "Jammu & Kashmir", "Moderate", 7, 4000),
    ("Nafran Valley", "Jammu & Kashmir", "Moderate", 7, 4100),
    ("Warwan Valley", "Jammu & Kashmir", "Hard", 8, 3800),
    ("Dzongri", "Sikkim", "Moderate", 5, 4020),
    ("Dzukou Valley", "Nagaland", "Easy", 3, 2452),
    ("Nongriat Root Bridge", "Meghalaya", "Easy", 2, 730),
    ("Chembra Peak", "Kerala", "Easy", 1, 2100),
    ("Kumara Parvatha", "Karnataka", "Moderate", 2, 1712),
    ("Kodachadri", "Karnataka", "Easy", 2, 1343),
    ("Tadiandamol", "Karnataka", "Easy", 1, 1748),
    ("Mullayanagiri", "Karnataka", "Easy", 1, 1930),
    ("Kudremukh", "Karnataka", "Moderate", 1, 1894),
    ("Rajmachi Fort", "Maharashtra", "Easy", 2, 820),
    ("Harishchandragad", "Maharashtra", "Moderate", 2, 1424),
    ("Kalsubai Peak", "Maharashtra", "Moderate", 1, 1646),
    ("Ratangad", "Maharashtra", "Moderate", 1, 1297),
    ("Kalavantin Durg", "Maharashtra", "Moderate", 1, 686),
    ("Torna Fort", "Maharashtra", "Moderate", 1, 1403),
    ("Sinhagad Fort", "Maharashtra", "Easy", 1, 1312),
    ("Visapur Fort", "Maharashtra", "Easy", 1, 1084),
    ("Lohagad Fort", "Maharashtra", "Easy", 1, 1033),
    ("Pindari Glacier", "Uttarakhand", "Moderate", 7, 3820),
    ("Milam Glacier", "Uttarakhand", "Hard", 10, 4000),
    ("Kedar Tal", "Uttarakhand", "Hard", 7, 4912),
    ("Bali Pass", "Uttarakhand", "Hard", 8, 4950),
    ("Pangarchulla Peak", "Uttarakhand", "Hard", 6, 4700),
]

with app.app_context():
    difficulty_slots = {"Easy": 25, "Moderate": 18, "Hard": 12}
    statuses = ["Approved", "Open", "Open", "Open", "Pending", "Closed"]

    count = 0
    for name, location, difficulty, duration, altitude in treks_data:
        if Trek.query.filter_by(name=name).first():
            continue
        total_slots = difficulty_slots[difficulty]
        start = date.today() + timedelta(days=random.randint(10, 120))
        end = start + timedelta(days=duration)
        status = random.choice(statuses)
        available = total_slots if status in ("Approved", "Open") else 0

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            total_slots=total_slots,
            available_slots=available,
            status=status,
            start_date=start,
            end_date=end,
            description=f"A {difficulty.lower()} trek to {name} in {location}, reaching an altitude of {altitude}m over {duration} day(s).",
            staff_id=None,
            created_by=1
        )
        db.session.add(trek)
        count += 1

    db.session.commit()
    print(f"Seeded {count} treks successfully.")