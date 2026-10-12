import database
from datetime import datetime, date

def seed_sample_data():
    database.init_db()
    existing = database.get_all_members()
    if len(existing) == 0:
        database.add_member(
            full_name="Alex Rivera",
            age=28,
            contact_number="0917-555-0192",
            membership_plan="Monthly",
            start_date_str="2026-09-01",
            payment_status="Paid",
            amount_paid=1500.00
        )
        database.add_member(
            full_name="Samantha Chen",
            age=34,
            contact_number="0918-555-0143",
            membership_plan="3 Months",
            start_date_str="2026-08-15",
            payment_status="Paid",
            amount_paid=4000.00
        )
        database.add_member(
            full_name="Marcus Vance",
            age=42,
            contact_number="0920-555-0178",
            membership_plan="Monthly",
            start_date_str="2026-08-01",
            payment_status="Paid",
            amount_paid=1500.00
        )
        database.add_member(
            full_name="Elena Rostova",
            age=23,
            contact_number="0919-555-0155",
            membership_plan="6 Months",
            start_date_str="2026-09-10",
            payment_status="Pending",
            amount_paid=0.00
        )
        database.add_member(
            full_name="David Miller",
            age=31,
            contact_number="0922-555-0189",
            membership_plan="1 Year",
            start_date_str="2026-01-10",
            payment_status="Paid",
            amount_paid=14000.00
        )
        print("Sample member records seeded successfully!")

if __name__ == "__main__":
    seed_sample_data()
