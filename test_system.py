import unittest
import os
import sqlite3
from datetime import datetime, date, timedelta
import database
import app

class TestGymMembershipSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use a temporary test database
        cls.test_db = os.path.join(os.path.dirname(__file__), 'test_gym.db')
        database.DB_PATH = cls.test_db
        app.app.config['TESTING'] = True
        cls.client = app.app.test_client()

    def setUp(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        database.init_db()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    # 1. Test Date Math & Plan Expiration Calculations
    def test_calculate_expiration_date(self):
        start = "2026-01-15"
        
        # Monthly -> 2026-02-15
        exp_m = database.calculate_expiration_date(start, "Monthly")
        self.assertEqual(exp_m.strftime("%Y-%m-%d"), "2026-02-15")
        
        # 3 Months -> 2026-04-15
        exp_3m = database.calculate_expiration_date(start, "3 Months")
        self.assertEqual(exp_3m.strftime("%Y-%m-%d"), "2026-04-15")
        
        # 6 Months -> 2026-07-15
        exp_6m = database.calculate_expiration_date(start, "6 Months")
        self.assertEqual(exp_6m.strftime("%Y-%m-%d"), "2026-07-15")
        
        # 1 Year -> 2027-01-15
        exp_1y = database.calculate_expiration_date(start, "1 Year")
        self.assertEqual(exp_1y.strftime("%Y-%m-%d"), "2027-01-15")

    # 2. Test Membership Status Logic (Active vs Expired)
    def test_membership_status_logic(self):
        future_date = (date.today() + timedelta(days=30)).strftime("%Y-%m-%d")
        past_date = (date.today() - timedelta(days=5)).strftime("%Y-%m-%d")

        self.assertEqual(database.get_membership_status(future_date), "Active")
        self.assertEqual(database.get_membership_status(past_date), "Expired")

    # 3. Test Add Member (Database Layer & Auto Member ID)
    def test_add_member(self):
        today_str = date.today().strftime("%Y-%m-%d")
        member = database.add_member(
            full_name="Jane Doe",
            age=26,
            contact_number="0917-111-2233",
            membership_plan="Monthly",
            start_date_str=today_str,
            payment_status="Paid",
            amount_paid=1500.00
        )
        self.assertIsNotNone(member)
        self.assertEqual(member['member_id'], "GYM-1001")
        self.assertEqual(member['full_name'], "Jane Doe")
        self.assertEqual(member['membership_status'], "Active")

        # Second member gets GYM-1002
        member2 = database.add_member(
            full_name="Bob Smith",
            age=30,
            contact_number="0918-222-3344",
            membership_plan="3 Months",
            start_date_str=today_str,
            payment_status="Pending",
            amount_paid=0.00
        )
        self.assertEqual(member2['member_id'], "GYM-1002")

    # 4. Test View All Members & Search
    def test_search_members(self):
        today_str = date.today().strftime("%Y-%m-%d")
        database.add_member("Carlos Sainz", 29, "0911-000-1111", "6 Months", today_str, "Paid", 5000.0)
        database.add_member("Lewis Hamilton", 38, "0922-000-2222", "1 Year", today_str, "Paid", 12000.0)

        # Search by Member ID
        res_id = database.search_members("GYM-1001")
        self.assertEqual(len(res_id), 1)
        self.assertEqual(res_id[0]['full_name'], "Carlos Sainz")

        # Search by partial Name
        res_name = database.search_members("Lewis")
        self.assertEqual(len(res_name), 1)
        self.assertEqual(res_name[0]['member_id'], "GYM-1002")

    # 5. Test Edit Member
    def test_update_member(self):
        today_str = date.today().strftime("%Y-%m-%d")
        m = database.add_member("Original Name", 20, "0900-000-0000", "Monthly", today_str, "Pending", 0.0)
        
        updated = database.update_member(
            db_id=m['id'],
            full_name="Updated Name",
            age=21,
            contact_number="0999-999-9999",
            membership_plan="3 Months",
            start_date_str=today_str,
            expiration_date_str=m['expiration_date'],
            payment_status="Paid",
            amount_paid=3000.0
        )
        self.assertEqual(updated['full_name'], "Updated Name")
        self.assertEqual(updated['age'], 21)
        self.assertEqual(updated['payment_status'], "Paid")

    # 6. Test Record Payment & Plan Extension
    def test_record_payment(self):
        today_str = date.today().strftime("%Y-%m-%d")
        m = database.add_member("Payment Test", 25, "0912-345-6789", "Monthly", today_str, "Pending", 0.0)
        
        # Record payment
        updated = database.record_payment(
            db_id=m['id'],
            amount_paid=1500.0,
            payment_status="Paid",
            payment_date_str=today_str,
            extend_plan="3 Months"
        )
        self.assertEqual(updated['payment_status'], "Paid")
        self.assertEqual(updated['amount_paid'], 1500.0)
        self.assertEqual(updated['membership_plan'], "3 Months")

    # 7. Test Delete Member
    def test_delete_member(self):
        today_str = date.today().strftime("%Y-%m-%d")
        m = database.add_member("To Be Deleted", 30, "0999-000-1111", "Monthly", today_str, "Paid", 1500.0)
        
        success = database.delete_member(m['id'])
        self.assertTrue(success)
        self.assertIsNone(database.get_member_by_db_id(m['id']))

    # 8. Test HTTP Endpoints & Form Validation
    def test_flask_add_member_validation(self):
        # Invalid Age (negative)
        res = self.client.post('/members/add', data={
            'full_name': 'Bad Age User',
            'age': '-5',
            'contact_number': '09170001111',
            'membership_plan': 'Monthly',
            'start_date': date.today().strftime("%Y-%m-%d"),
            'payment_status': 'Paid',
            'amount_paid': '1000'
        }, follow_redirects=True)
        self.assertIn(b'Age must be between 1 and 120.', res.data)

        # Missing Name
        res2 = self.client.post('/members/add', data={
            'full_name': '',
            'age': '25',
            'contact_number': '09170001111',
            'membership_plan': 'Monthly',
            'start_date': date.today().strftime("%Y-%m-%d"),
            'payment_status': 'Paid',
            'amount_paid': '1000'
        }, follow_redirects=True)
        self.assertIn(b'Full Name is required.', res2.data)

if __name__ == '__main__':
    unittest.main()
