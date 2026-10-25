import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from restaurants.model import Restaurant


def populate_database():
    csv_file_path = "csv/restaurants_202504091426.csv"
    df = pd.read_csv(csv_file_path)
    restaurant_objects = [
        Restaurant(**row.to_dict())
        for _, row in df.iterrows()
    ]

    db: Session = SessionLocal()
    try:
        db.add_all(restaurant_objects)
        db.commit()
        print(f"{len(restaurant_objects)} restaurants inserted into the database.")
    except Exception as e:
        db.rollback()
        print("Error inserting into DB:", e)
    finally:
        db.close()

populate_database()
