from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import database
import sample_data
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = 'gym_management_super_secret_key'

# Initialize database on application start
database.init_db()
sample_data.seed_sample_data()

VALID_PLANS = ["Monthly", "3 Months", "6 Months", "1 Year"]
VALID_PAYMENT_STATUSES = ["Paid", "Pending", "Overdue"]

@app.route('/')
@app.route('/dashboard')
def dashboard():
    stats = database.get_dashboard_stats()
    all_members = database.get_all_members()
    recent_members = all_members[:5]
    expired_members = [m for m in all_members if m['membership_status'] == 'Expired']
    pending_payments = [m for m in all_members if m['payment_status'] in ['Pending', 'Overdue']]
    
    return render_template(
        'dashboard.html',
        stats=stats,
        recent_members=recent_members,
        expired_members=expired_members,
        pending_payments=pending_payments,
        active_page='dashboard'
    )

@app.route('/members')
def members_list():
    filter_type = request.args.get('filter', 'all')
    all_members = database.get_all_members()
    
    if filter_type == 'active':
        members = [m for m in all_members if m['membership_status'] == 'Active']
    elif filter_type == 'expired':
        members = [m for m in all_members if m['membership_status'] == 'Expired']
    elif filter_type == 'pending':
        members = [m for m in all_members if m['payment_status'] in ['Pending', 'Overdue']]
    else:
        members = all_members
        
    return render_template('members.html', members=members, filter_type=filter_type, active_page='members')

@app.route('/members/add', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        age_str = request.form.get('age', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        membership_plan = request.form.get('membership_plan', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        payment_status = request.form.get('payment_status', '').strip()
        amount_paid_str = request.form.get('amount_paid', '0').strip()

        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                errors.append("Age must be between 1 and 120.")
        except ValueError:
            errors.append("Please enter a valid numeric Age.")
            
        if not contact_number:
            errors.append("Contact Number is required.")
            
        if membership_plan not in VALID_PLANS:
            errors.append(f"Invalid Membership Plan. Must be one of: {', '.join(VALID_PLANS)}")
            
        if not start_date_str:
            errors.append("Start Date is required.")
        else:
            try:
                datetime.strptime(start_date_str, "%Y-%m-%d")
            except ValueError:
                errors.append("Invalid Start Date format (YYYY-MM-DD required).")
                
        if payment_status not in VALID_PAYMENT_STATUSES:
            errors.append("Payment Status must be Paid, Pending, or Overdue.")
            
        try:
            amount_paid = float(amount_paid_str) if amount_paid_str else 0.0
            if amount_paid < 0:
                errors.append("Amount paid cannot be negative.")
        except ValueError:
            errors.append("Amount paid must be a valid number.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'add_member.html',
                form_data=request.form,
                plans=VALID_PLANS,
                statuses=VALID_PAYMENT_STATUSES,
                today=date.today().strftime("%Y-%m-%d"),
                active_page='add_member'
            )

        new_member = database.add_member(
            full_name=full_name,
            age=age,
            contact_number=contact_number,
            membership_plan=membership_plan,
            start_date_str=start_date_str,
            payment_status=payment_status,
            amount_paid=amount_paid
        )
        flash(f"Member '{new_member['full_name']}' added successfully with ID {new_member['member_id']}!", "success")
        return redirect(url_for('members_list'))

    today_str = date.today().strftime("%Y-%m-%d")
    return render_template(
        'add_member.html',
        form_data={'start_date': today_str, 'amount_paid': '0'},
        plans=VALID_PLANS,
        statuses=VALID_PAYMENT_STATUSES,
        today=today_str,
        active_page='add_member'
    )

@app.route('/members/edit/<int:db_id>', methods=['GET', 'POST'])
def edit_member(db_id):
    member = database.get_member_by_db_id(db_id)
    if not member:
        flash("Member record not found.", "danger")
        return redirect(url_for('members_list'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        age_str = request.form.get('age', '').strip()
        contact_number = request.form.get('contact_number', '').strip()
        membership_plan = request.form.get('membership_plan', '').strip()
        start_date_str = request.form.get('start_date', '').strip()
        expiration_date_str = request.form.get('expiration_date', '').strip()
        payment_status = request.form.get('payment_status', '').strip()
        amount_paid_str = request.form.get('amount_paid', '0').strip()

        errors = []
        if not full_name:
            errors.append("Full Name is required.")
        
        try:
            age = int(age_str)
            if age <= 0 or age > 120:
                errors.append("Age must be between 1 and 120.")
        except ValueError:
            errors.append("Please enter a valid numeric Age.")

        if not contact_number:
            errors.append("Contact Number is required.")

        if membership_plan not in VALID_PLANS:
            errors.append(f"Invalid Membership Plan. Must be one of: {', '.join(VALID_PLANS)}")

        if not start_date_str or not expiration_date_str:
            errors.append("Start Date and Expiration Date are required.")
        else:
            try:
                datetime.strptime(start_date_str, "%Y-%m-%d")
                datetime.strptime(expiration_date_str, "%Y-%m-%d")
            except ValueError:
                errors.append("Dates must follow YYYY-MM-DD format.")

        if payment_status not in VALID_PAYMENT_STATUSES:
            errors.append("Payment Status must be Paid, Pending, or Overdue.")

        try:
            amount_paid = float(amount_paid_str)
        except ValueError:
            errors.append("Amount Paid must be a valid number.")

        if errors:
            for err in errors:
                flash(err, 'danger')
            return render_template(
                'edit_member.html',
                member=member,
                plans=VALID_PLANS,
                statuses=VALID_PAYMENT_STATUSES,
                active_page='members'
            )

        database.update_member(
            db_id=db_id,
            full_name=full_name,
            age=age,
            contact_number=contact_number,
            membership_plan=membership_plan,
            start_date_str=start_date_str,
            expiration_date_str=expiration_date_str,
            payment_status=payment_status,
            amount_paid=amount_paid
        )
        flash(f"Member '{full_name}' ({member['member_id']}) updated successfully.", "success")
        return redirect(url_for('members_list'))

    return render_template(
        'edit_member.html',
        member=member,
        plans=VALID_PLANS,
        statuses=VALID_PAYMENT_STATUSES,
        active_page='members'
    )

@app.route('/members/delete/<int:db_id>', methods=['POST'])
def delete_member(db_id):
    member = database.get_member_by_db_id(db_id)
    if not member:
        flash("Member record not found.", "danger")
        return redirect(url_for('members_list'))
    
    member_name = member['full_name']
    member_code = member['member_id']
    if database.delete_member(db_id):
        flash(f"Member '{member_name}' ({member_code}) was deleted.", "info")
    else:
        flash("Failed to delete member record.", "danger")
    return redirect(url_for('members_list'))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    results = database.search_members(query) if query else database.get_all_members()
    return render_template('search.html', query=query, results=results, active_page='search')

@app.route('/payments', methods=['GET', 'POST'])
def payments():
    if request.method == 'POST':
        db_id_str = request.form.get('member_id', '').strip()
        amount_paid_str = request.form.get('amount_paid', '0').strip()
        payment_status = request.form.get('payment_status', 'Paid').strip()
        extend_plan = request.form.get('extend_plan', '').strip() or None
        payment_date = date.today().strftime("%Y-%m-%d")

        try:
            db_id = int(db_id_str)
            amount_paid = float(amount_paid_str)
            if amount_paid < 0:
                flash("Amount paid cannot be negative.", "danger")
                return redirect(url_for('payments'))
        except ValueError:
            flash("Invalid member selection or payment amount.", "danger")
            return redirect(url_for('payments'))

        member = database.record_payment(
            db_id=db_id,
            amount_paid=amount_paid,
            payment_status=payment_status,
            payment_date_str=payment_date,
            extend_plan=extend_plan
        )

        if member:
            msg = f"Payment of ₱{amount_paid:,.2f} recorded for {member['full_name']} ({member['member_id']}). Status is now '{payment_status}'."
            if extend_plan:
                msg += f" Membership extended ({extend_plan}) until {member['expiration_date']}!"
            flash(msg, "success")
        else:
            flash("Failed to record payment. Member not found.", "danger")

        return redirect(url_for('payments'))

    members = database.get_all_members()
    return render_template('payments.html', members=members, plans=VALID_PLANS, statuses=VALID_PAYMENT_STATUSES, active_page='payments')

@app.route('/status')
def membership_status():
    all_members = database.get_all_members()
    active_members = [m for m in all_members if m['membership_status'] == 'Active']
    expired_members = [m for m in all_members if m['membership_status'] == 'Expired']
    
    return render_template(
        'status.html',
        active_members=active_members,
        expired_members=expired_members,
        active_page='status'
    )

# --- API Endpoints ---
@app.route('/api/calculate-expiration', methods=['POST'])
def api_calculate_expiration():
    data = request.json or {}
    start_date_str = data.get('start_date')
    plan = data.get('plan')
    
    if not start_date_str or not plan:
        return jsonify({'error': 'Missing start_date or plan'}), 400
        
    try:
        exp_date = database.calculate_expiration_date(start_date_str, plan)
        return jsonify({'expiration_date': exp_date.strftime("%Y-%m-%d")})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/search')
def api_search():
    query = request.args.get('q', '').strip()
    results = database.search_members(query)
    return jsonify(results)

if __name__ == '__main__':
    print("Starting Pulse Gym Management System on http://127.0.0.1:5000 and http://localhost:5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
