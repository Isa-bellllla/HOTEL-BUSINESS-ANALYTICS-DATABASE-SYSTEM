import os
import random
import secrets
import sqlite3
from datetime import date, datetime, timedelta
from math import isfinite
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from hotel_catalog import DINING_DISCOUNT, EXTENDED_CHECKOUT_RATE, FACILITIES, FACILITY_SECTIONS, ROOM_TYPES, update_catalog

app = Flask(__name__)
app.secret_key = os.environ.get("HOTEL_SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
PROJECT_ROOT = Path(__file__).resolve().parent
DB_NAME = os.environ.get("HOTEL_DB_PATH") or PROJECT_ROOT / "hotel.db"
ROLES = {"customer": "Customer", "staff": "Staff", "manager": "Manager"}
HOTEL_TIMEZONE = ZoneInfo("America/Los_Angeles")
MAX_GUESTS = max(room[2] for _, room in ROOM_TYPES)
SLOT_LABELS = {
    "Morning": "Morning · 8:00–11:30 AM",
    "Lunch": "Lunch · 12:00–2:00 PM",
    "Afternoon": "Afternoon · 2:30–5:30 PM",
    "Evening": "Evening · 6:00–9:00 PM",
    "Night": "Night · 9:00–11:30 PM",
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.executescript((PROJECT_ROOT / "Database.sql").read_text(encoding="utf-8"))
    cursor.execute("BEGIN IMMEDIATE")
    cursor.execute('SELECT COUNT(*) FROM user')
    if cursor.fetchone()[0] == 0:
        for s in ['Morning', 'Lunch', 'Afternoon', 'Evening', 'Night']:
            cursor.execute('INSERT INTO facility_time_slot (slot_name) VALUES (?)', (s,))
        cursor.execute("INSERT INTO building (building_name, floors_count) VALUES ('The Main House', 5)")
        cursor.execute("INSERT INTO building (building_name, floors_count) VALUES ('The Garden Annex', 4)")
        for b_id, w_code, p_pool, p_pkg, hcap in [(1, 'East Wing', 'Courtyard Pool', 'East Lot', 1), (1, 'West Wing', 'Sun Patio', 'West Garage', 1), (2, 'Garden Wing', 'Bathhouse Garden', 'South Lot', 1), (2, 'Pine Wing', 'Forest Walk', 'Main Gate', 1)]:
            cursor.execute('INSERT INTO wing (building_id, wing_code, proximity_pool, proximity_parking, has_handicap_access) VALUES (?,?,?,?,?)', (b_id, w_code, p_pool, p_pkg, hcap))
        for _, room_type in ROOM_TYPES:
            cursor.execute('INSERT INTO room_type (type_name, base_rate, max_occupancy, is_suite, description, image_url) VALUES (?,?,?,?,?,?)', room_type)
        for w_id in range(1, 5):
            for fl in range(1, 4):
                for rm in range(1, 4):
                    st = random.choice(['Clean/Vacant', 'Occupied', 'Clean/Vacant', 'Maintenance/Dirty'])
                    cursor.execute('INSERT INTO room (wing_id, room_number, floor_num, room_type_id, is_nonsmoking, has_toilet, status) VALUES (?,?,?,?,?,?,?)', (w_id, f'{fl}0{rm}', fl, random.choice([1, 2, 3, 4]), 1, 1, st))
        for _, facility in FACILITIES:
            cursor.execute('INSERT INTO facility (facility_name, facility_type, hourly_rate, capacity, description, image_url) VALUES (?,?,?,?,?,?)', facility)
        cursor.execute("INSERT INTO user (username, password, role, full_name, phone, email) VALUES ('manager', 'manager123', 'manager', 'Claire Miller (Operations Lead)', '212-555-0101', 'claire.m@thehaven.com')")
        cursor.execute("INSERT INTO user (username, password, role, full_name, phone, email) VALUES ('staff', 'staff123', 'staff', 'Tom Harris (Front Desk)', '212-555-0102', 'tom.h@thehaven.com')")
        cursor.execute('INSERT INTO staff (user_id, department, position) VALUES (2, "Front Desk", "Host")')
        for s_idx, (s_n, dept) in enumerate([('Leo Chen', 'Guest Services'), ('Maya Lin', 'Bathhouse & Spa'), ('Sam Taylor', 'Kitchen & Cafe')], start=3):
            cursor.execute('INSERT INTO user (username, password, role, full_name, phone, email) VALUES (?, "staff123", "staff", ?, "212-555-0109", ?)', (f'staff_{s_idx}', s_n, f'{s_n.lower().replace(" ", ".")}@thehaven.com'))
            cursor.execute('INSERT INTO staff (user_id, department, position) VALUES (?, ?, "Associate")', (s_idx, dept))
        cursor.execute("INSERT INTO user (username, password, role, full_name, phone, email) VALUES ('customer', 'customer123', 'customer', 'Julian Vance', '415-889-1234', 'julian.vance@gmail.com')")
        cursor.execute("INSERT INTO customer (user_id, organization_name, vip_level, advance_deposit_required) VALUES (6, 'Studio Design Lab', 'Member', 0)")
        cursor.execute('INSERT INTO billing_account (customer_id, total_charges, total_paid) VALUES (1, 0.0, 0.0)')
        fnames = ['James', 'Emma', 'Oliver', 'Sophia', 'Lucas', 'Isabella', 'Ethan', 'Mia', 'Aiden', 'Charlotte', 'Liam', 'Ava', 'Noah', 'Amelia', 'Mason', 'Harper', 'Logan', 'Evelyn']
        lnames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez', 'Wilson', 'Anderson']
        orgs = ['Design Collective', 'Kite Studio', 'North Arch', 'Urban Field Lab', 'Craft Works', 'Open Media', 'None']
        base_d = datetime(2025, 1, 1)
        for i in range(1, 82):
            fn = f'{random.choice(fnames)} {random.choice(lnames)}'
            org = random.choice(orgs)
            vip = random.choices(['Standard', 'Frequent Guest', 'Club Member'], weights=[65, 25, 10])[0]
            cursor.execute('INSERT INTO user (username, password, role, full_name, phone, email) VALUES (?, "123456", "customer", ?, ?, ?)', (f'guest_{i}', fn, f'555-01{i:02d}', f'guest_{i}@havenstay.com'))
            u_id = cursor.lastrowid
            cursor.execute('INSERT INTO customer (user_id, organization_name, vip_level, advance_deposit_required) VALUES (?, ?, ?, 0)', (u_id, org if org != 'None' else None, vip))
            cursor.execute('INSERT INTO billing_account (customer_id, total_charges, total_paid) VALUES (?, 0.0, 0.0)', (cursor.lastrowid,))
        item_pool = [
            ('Room Rent', 'Guestroom Stay', [160.0, 240.0, 320.0]),
            ('Mini Bar', 'Sparkling Water, Local Cider & Granola Pack', [8.0, 15.0, 24.0, 32.0]),
            ('Asian Food', 'Nami Hand-Pulled Ramen & Pork Donburi', [22.0, 42.0, 68.0]),
            ('Spain Food', 'Casa Olivo Grilled Chorizo & House Red Wine', [28.0, 45.0, 72.0]),
            ('Western Brunch', 'Avocado Sourdough, Poached Eggs & Oat Milk Latte', [18.0, 34.0, 52.0]),
            ('Neighborhood Bistro', 'Roast Farm Chicken & Warm Apple Crumble', [36.0, 58.0, 88.0]),
            ('Board Game / Social Lounge', 'Club Room Game Table & Snack Caddy', [16.0, 28.0, 40.0]),
            ('Bathhouse & Spa', 'Cedar Steam Bath & Lavender Salt Scrub', [35.0, 60.0, 90.0]),
            ('Meeting Room', 'Library Room Half-Day Creative Session', [120.0, 240.0, 320.0]),
            ('Event Hall', 'North Forum Afternoon Workshop Booking', [350.0, 560.0, 840.0])
        ]
        for _ in range(180):
            cid = random.randint(1, 80)
            cursor.execute('SELECT account_id FROM billing_account WHERE customer_id = ?', (cid,))
            acc_id = cursor.fetchone()[0]
            rid = random.randint(1, 24)
            cin = base_d + timedelta(days=random.randint(5, 350))
            stay_days = random.randint(1, 4)
            cout = cin + timedelta(days=stay_days)
            cursor.execute('SELECT rt.base_rate FROM room r JOIN room_type rt ON r.room_type_id = rt.type_id WHERE r.room_id = ?', (rid,))
            rate = cursor.fetchone()[0]
            room_cost = rate * stay_days
            cursor.execute('INSERT INTO room_reservation (customer_id, room_id, billing_account_id, check_in_date, check_out_date, duration_days, reservation_status) VALUES (?,?,?,?,?,?,"Confirmed")', (cid, rid, acc_id, cin.strftime('%Y-%m-%d'), cout.strftime('%Y-%m-%d'), stay_days))
            reservation_id = cursor.lastrowid
            cursor.execute('INSERT INTO billing_item (account_id, item_category, description, amount, trans_time) VALUES (?, "Room Rent", ?, ?, ?)', (acc_id, f'Stay of {stay_days} nights in Room #{rid}', room_cost, cin.strftime('%Y-%m-%d 15:00:00')))
            extra_cost = 0.0
            for cat_n, cat_d, pr_list in random.sample(item_pool[1:], random.randint(2, 4)):
                p_amt = random.choice(pr_list)
                tx_time = cin + timedelta(hours=random.randint(4, 36))
                cursor.execute('INSERT INTO billing_item (account_id, item_category, description, amount, trans_time) VALUES (?, ?, ?, ?, ?)', (acc_id, cat_n, cat_d, p_amt, tx_time.strftime('%Y-%m-%d %H:%M:%S')))
                extra_cost += p_amt
            total_cost = room_cost + extra_cost
            paid_cost = total_cost if random.random() > 0.1 else total_cost * random.choice([0.0, 0.5])
            cursor.execute('UPDATE billing_account SET total_charges = total_charges + ?, total_paid = total_paid + ? WHERE account_id = ?', (total_cost, paid_cost, acc_id))
            if paid_cost > 0:
                cursor.execute('INSERT INTO payment (account_id, amount, payment_method, card_last4, cardholder_name, payment_time, payment_status) VALUES (?, ?, "Credit Card", "4321", "Verified Guest", ?, "Success")', (acc_id, paid_cost, (cout - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S')))
            if random.random() > 0.4:
                cursor.execute('INSERT INTO room_request (reservation_id, request_type, details, status, created_time) VALUES (?, ?, "Guest in-room note", ?, ?)', (reservation_id, random.choice(['Restock Mini Bar Waters', 'Extra Cotton Pillows', 'Late Check-out 1h', 'Board Game Delivery']), random.choice(['Pending', 'In Progress', 'Completed']), cin.strftime('%Y-%m-%d 18:30:00')))
            cursor.execute('INSERT INTO facility_usage_log (customer_id, facility_id, action, scan_time) VALUES (?, ?, "IN", ?)', (cid, random.randint(1, 9), cin.strftime('%Y-%m-%d 12:30:00')))
            if random.random() > 0.4:
                cursor.execute('INSERT INTO service_feedback (customer_id, staff_id, rating, comments, feedback_date) VALUES (?, ?, ?, "Warm, understated space and attentive hosts.", ?)', (cid, random.randint(1, 4), random.choices([5, 4, 3], weights=[75, 20, 5])[0], cout.strftime('%Y-%m-%d')))
    update_catalog(conn)
    conn.commit()
    conn.close()


def hotel_today():
    return datetime.now(HOTEL_TIMEZONE).date()


def stay_params(values):
    today = hotel_today()
    check_in = date.fromisoformat(values.get("check_in") or today.isoformat())
    check_out = date.fromisoformat(values.get("check_out") or (check_in + timedelta(days=1)).isoformat())
    guests = int(values.get("guests") or 2)
    if check_in < today or check_out <= check_in or not 1 <= guests <= MAX_GUESTS:
        raise ValueError("Choose a future stay with check-out after check-in and a valid guest count.")
    return {"check_in": check_in.isoformat(), "check_out": check_out.isoformat(), "guests": guests}


def available_rooms(conn, stay, room_id=None):
    return conn.execute(
        """SELECT r.room_id, r.room_number, r.floor_num, w.wing_code,
                  rt.type_id, rt.type_name, rt.base_rate
           FROM room r JOIN room_type rt ON r.room_type_id = rt.type_id
           JOIN wing w ON w.wing_id = r.wing_id
           WHERE r.status = 'Clean/Vacant' AND rt.max_occupancy >= :guests
             AND (:room_id IS NULL OR r.room_id = :room_id)
             AND NOT EXISTS (
                 SELECT 1 FROM room_reservation rr
                 WHERE rr.room_id = r.room_id AND rr.reservation_status = 'Confirmed'
                   AND rr.check_in_date < :check_out AND rr.check_out_date > :check_in
             )
           ORDER BY rt.base_rate, w.wing_code, r.room_number""",
        {**stay, "room_id": room_id},
    ).fetchall()


def stay_values(values):
    keys = ("check_in", "check_out", "guests", "room_type", "facility_id")
    return {key: values[key] for key in keys if values.get(key)}


def stay_link(endpoint, values, **extras):
    return url_for(endpoint, **stay_values(values), **extras)


@app.route("/")
def index():
    conn = get_db()
    room_types = conn.execute("SELECT * FROM room_type ORDER BY base_rate").fetchall()
    facilities = conn.execute("SELECT * FROM facility ORDER BY facility_id").fetchall()
    conn.close()
    sections = [
        (section_id, title, headline, [(f, labels[f["facility_type"]]) for f in facilities if f["facility_type"] in labels])
        for section_id, title, headline, labels in FACILITY_SECTIONS
    ]
    known_types = {key for _, _, _, labels in FACILITY_SECTIONS for key in labels}
    other = [(f, f["facility_type"]) for f in facilities if f["facility_type"] not in known_types]
    if other:
        sections.append(("other-spaces", "More spaces", "Explore the hotel.", other))
    return render_template("index.html", room_types=room_types, sections=sections, stay=stay_params({}),
                           today=hotel_today().isoformat(), max_guests=MAX_GUESTS)


@app.route("/suites")
def suites_page():
    searching = any(request.args.get(key) for key in ("check_in", "check_out", "guests"))
    try:
        stay = stay_params(request.args)
    except (ValueError, OverflowError):
        flash("Choose valid dates and a guest count to check availability.")
        return redirect(url_for("suites_page"))
    conn = get_db()
    room_types = conn.execute("SELECT * FROM room_type ORDER BY base_rate").fetchall()
    if searching:
        open_types = {room["type_id"] for room in available_rooms(conn, stay)}
        room_types = [room_type for room_type in room_types if room_type["type_id"] in open_types]
    conn.close()
    return render_template("suites.html", room_types=room_types, stay=stay, searching=searching,
                           today=hotel_today().isoformat(), max_guests=MAX_GUESTS)


@app.route("/login")
def login_page():
    role = request.args.get("role", "customer")
    if role not in ROLES:
        role = "customer"
    register = role == "customer" and request.args.get("register") == "1"
    return render_template("login.html", role=role, roles=ROLES, register=register, continuation=stay_values(request.args))


@app.route("/auth", methods=["POST"])
def auth():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    role = request.form.get("role", "customer")
    register = request.form.get("action") == "register"
    if role not in ROLES or (register and role != "customer"):
        flash("Choose a valid account type.")
        return redirect(url_for("login_page"))

    login_url = stay_link("login_page", request.form, role=role, register="1" if register else None)
    if not username or not password:
        flash("Enter a username and password.")
        return redirect(login_url)

    conn = get_db()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            user = conn.execute("SELECT * FROM user WHERE username = ?", (username,)).fetchone()
            if register:
                if user:
                    flash("That username is already in use.")
                    return redirect(login_url)
                if len(password) < 8:
                    flash("Use a password with at least eight characters.")
                    return redirect(login_url)
                full_name = request.form.get("full_name", "").strip() or username
                user_id = conn.execute(
                    """INSERT INTO user (username, password, role, full_name, phone, email)
                       VALUES (?, ?, 'customer', ?, '555-0199', ?)""",
                    (username, generate_password_hash(password), full_name, f"{username}@thehaven.com"),
                ).lastrowid
                customer_id = conn.execute(
                    "INSERT INTO customer (user_id, organization_name, vip_level) VALUES (?, 'Personal Resident', 'Standard')",
                    (user_id,),
                ).lastrowid
                conn.execute("INSERT INTO billing_account (customer_id) VALUES (?)", (customer_id,))
                user = conn.execute("SELECT * FROM user WHERE user_id = ?", (user_id,)).fetchone()
            elif not user or user["role"] != role or not password_matches(user["password"], password):
                flash("The username or password does not match this account type.")
                return redirect(login_url)
            elif not user["password"].startswith(("scrypt:", "pbkdf2:")):
                conn.execute("UPDATE user SET password = ? WHERE user_id = ?",
                             (generate_password_hash(password), user["user_id"]))
    finally:
        conn.close()

    session.clear()
    session.update({key: user[key] for key in ("user_id", "username", "role", "full_name")})
    if role == "customer":
        destination = "facility-booking" if request.form.get("facility_id") else "room-booking"
        return redirect(stay_link("customer_portal", request.form, _anchor=destination))
    return redirect(url_for(f"{role}_portal"))


def password_matches(stored, supplied):
    if not stored:
        return False
    if stored.startswith(("scrypt:", "pbkdf2:")):
        return check_password_hash(stored, supplied)
    return secrets.compare_digest(stored.encode(), supplied.encode())


@app.route("/logout")
def logout():
    session.clear()
    flash("You’ve been signed out.")
    return redirect(url_for("index"))


@app.route("/customer")
def customer_portal():
    if session.get("role") != "customer":
        return redirect(stay_link("login_page", request.args, role="customer"))
    try:
        stay = stay_params(request.args)
    except (ValueError, OverflowError):
        flash("Choose valid dates and a guest count.")
        return redirect(url_for("customer_portal"))
    conn = get_db()
    facilities = conn.execute("SELECT * FROM facility ORDER BY facility_name").fetchall()
    rooms = available_rooms(conn, stay)
    time_slots = [row["slot_name"] for row in conn.execute("SELECT slot_name FROM facility_time_slot ORDER BY slot_id")]
    cust_account = conn.execute(
        """SELECT ba.* FROM customer c JOIN billing_account ba ON ba.customer_id = c.customer_id
           WHERE c.user_id = ?""", (session["user_id"],)
    ).fetchone()
    cust_items = conn.execute(
        "SELECT * FROM billing_item WHERE account_id = ? ORDER BY trans_time DESC", (cust_account["account_id"],)
    ).fetchall()
    conn.close()
    room_type = request.args.get("room_type", type=int)
    facility_id = request.args.get("facility_id", type=int)
    selected_room = next((room["room_id"] for room in rooms if room["type_id"] == room_type), None)
    if room_type is not None and selected_room is None:
        flash("That room type is unavailable for these dates. You can check other dates or select another room.")
    return render_template("portal.html", view_mode="customer", facilities=facilities, available_rooms=rooms,
                           cust_account=cust_account, cust_items=cust_items, stay=stay, selected_room=selected_room,
                           time_slots=[(slot, SLOT_LABELS.get(slot, slot)) for slot in time_slots],
                           selected_facility=facility_id, today=hotel_today().isoformat(), max_guests=MAX_GUESTS,
                           extended_checkout_rate=EXTENDED_CHECKOUT_RATE, dining_discount=DINING_DISCOUNT)


@app.route("/customer/reserve_room", methods=["POST"])
def customer_reserve_room():
    if session.get("role") != "customer":
        return redirect(url_for("login_page", role="customer"))
    try:
        stay = stay_params(request.form)
        room_id = int(request.form.get("room_id", ""))
        ext_hours = int(request.form.get("extension_hours", 0))
        if ext_hours not in (0, 2, 4) or not request.form.get("check_in") or not request.form.get("check_out"):
            raise ValueError
    except (ValueError, OverflowError):
        flash("Choose an available room, valid dates and a check-out option.")
        return redirect(url_for("customer_portal"))

    check_in, check_out = stay["check_in"], stay["check_out"]
    stay_days = (date.fromisoformat(check_out) - date.fromisoformat(check_in)).days
    conn = get_db()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            rooms = available_rooms(conn, stay, room_id)
            if not rooms:
                flash("That room is no longer available for your stay. Please choose another room.")
                return redirect(stay_link("customer_portal", stay))
            room = rooms[0]
            account = conn.execute(
                """SELECT c.customer_id, ba.account_id FROM customer c
                   JOIN billing_account ba ON ba.customer_id = c.customer_id WHERE c.user_id = ?""",
                (session["user_id"],),
            ).fetchone()
            surcharge = EXTENDED_CHECKOUT_RATE if ext_hours > 2 else 0
            rate = room["base_rate"]
            total_cost = round(rate * stay_days + surcharge, 2)
            conn.execute(
                """INSERT INTO room_reservation (customer_id, room_id, billing_account_id, check_in_date,
                   check_out_date, duration_days, extension_hours, extension_surcharge, reservation_status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Confirmed')""",
                (account["customer_id"], room_id, account["account_id"], check_in, check_out, stay_days, ext_hours, surcharge),
            )
            description = f'{room["type_name"]} · {room["wing_code"]} #{room["room_number"]} ({stay_days} nights @ ${rate:,.2f}/night)'
            conn.execute(
                """INSERT INTO billing_item (account_id, item_category, description, amount, trans_time)
                   VALUES (?, 'Room Rent', ?, ?, CURRENT_TIMESTAMP)""",
                (account["account_id"], description, total_cost),
            )
            conn.execute("UPDATE billing_account SET total_charges = total_charges + ? WHERE account_id = ?",
                         (total_cost, account["account_id"]))
    finally:
        conn.close()
    flash(f"Your {stay_days}-night stay is confirmed. ${total_cost:,.2f} was added to your folio.")
    return redirect(url_for("customer_portal"))


@app.route("/customer/reserve_facility", methods=["POST"])
def customer_reserve_facility():
    if session.get("role") != "customer":
        return redirect(url_for("login_page", role="customer"))
    facility_id = request.form.get("facility_id", type=int)
    slot_name = request.form.get("slot_name")
    try:
        res_date = date.fromisoformat(request.form.get("res_date", ""))
        duration = int(request.form.get("duration_hours", 2))
        is_eating = int(request.form.get("is_eating", 0))
        if res_date < hotel_today() or not 1 <= duration <= 8 or is_eating not in (0, 1):
            raise ValueError
    except ValueError:
        flash("Choose a valid date, time slot and duration.")
        return redirect(url_for("customer_portal", facility_id=facility_id))

    conn = get_db()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            facility = conn.execute("SELECT * FROM facility WHERE facility_id = ?", (facility_id,)).fetchone()
            slot = conn.execute("SELECT 1 FROM facility_time_slot WHERE slot_name = ?", (slot_name,)).fetchone()
            if not facility or not slot:
                flash("Choose a valid space and time slot.")
                return redirect(url_for("customer_portal", facility_id=facility_id))
            account = conn.execute(
                """SELECT c.customer_id, ba.account_id FROM customer c
                   JOIN billing_account ba ON ba.customer_id = c.customer_id WHERE c.user_id = ?""",
                (session["user_id"],),
            ).fetchone()
            base_charge = round(facility["hourly_rate"] * duration, 2)
            discount = round(base_charge * DINING_DISCOUNT, 2) if is_eating else 0
            final_charge = round(base_charge - discount, 2)
            conn.execute(
                """INSERT INTO facility_reservation (customer_id, facility_id, res_date, slot_name,
                   duration_hours, is_eating_usage, base_charge, discount_amount, final_charge)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (account["customer_id"], facility_id, res_date.isoformat(), slot_name,
                 duration, is_eating, base_charge, discount, final_charge),
            )
            description = f'{facility["facility_name"]} ({duration}h on {res_date})'
            conn.execute(
                """INSERT INTO billing_item (account_id, item_category, description, amount, trans_time)
                   VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                (account["account_id"], facility["facility_type"], description, final_charge),
            )
            conn.execute("UPDATE billing_account SET total_charges = total_charges + ? WHERE account_id = ?",
                         (final_charge, account["account_id"]))
    finally:
        conn.close()
    flash(f'{facility["facility_name"]} is reserved. ${final_charge:,.2f} was added to your folio.')
    return redirect(url_for("customer_portal"))


@app.route("/customer/pay", methods=["POST"])
def customer_pay():
    if session.get("role") != "customer":
        return redirect(url_for("login_page", role="customer"))
    amount = request.form.get("amount", type=float)
    billing_type = request.form.get("billing_type", "Personal")
    cardholder = request.form.get("cardholder_name", "").strip()
    card_number = request.form.get("card_number", "").replace(" ", "")
    if (amount is None or not isfinite(amount) or round(amount, 2) <= 0 or
            billing_type not in ("Personal", "Corporate") or not cardholder or
            len(card_number) != 16 or not card_number.isascii() or not card_number.isdecimal()):
        flash("Enter a valid payment amount and test card details.")
        return redirect(url_for("customer_portal"))

    amount = round(amount, 2)
    last4 = card_number[-4:]
    conn = get_db()
    try:
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            account = conn.execute(
                """SELECT ba.* FROM customer c JOIN billing_account ba ON ba.customer_id = c.customer_id
                   WHERE c.user_id = ?""", (session["user_id"],)
            ).fetchone()
            balance = round(account["total_charges"] - account["total_paid"], 2)
            if amount > balance:
                flash("The payment amount exceeds your current folio balance.")
                return redirect(url_for("customer_portal"))
            conn.execute(
                """INSERT INTO payment (account_id, amount, payment_method, card_last4, cardholder_name,
                   payment_time, payment_status) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'Success')""",
                (account["account_id"], amount, f"{billing_type} Card", last4, cardholder),
            )
            conn.execute("UPDATE billing_account SET total_paid = total_paid + ? WHERE account_id = ?",
                         (amount, account["account_id"]))
    finally:
        conn.close()
    flash(f"Demo payment of ${amount:,.2f} recorded for card ending in {last4}.")
    return redirect(url_for("customer_portal"))


@app.route("/staff")
def staff_portal():
    if session.get('role') not in ('staff', 'manager'):
        return redirect(url_for('login_page', role='staff'))
    conn = get_db()
    cursor = conn.cursor()
    today = hotel_today().isoformat()
    cursor.execute('''
        SELECT u.full_name, u.phone, u.email, c.organization_name, r.room_number, w.wing_code,
               rr.check_in_date, rr.check_out_date, rr.duration_days, ba.total_charges, ba.total_paid,
               CASE WHEN rr.reservation_status = 'Confirmed' AND rr.check_in_date <= :today AND rr.check_out_date > :today
                    THEN 'Occupied' ELSE r.status END AS status
        FROM room_reservation rr
        JOIN customer c ON rr.customer_id = c.customer_id
        JOIN user u ON c.user_id = u.user_id
        JOIN room r ON rr.room_id = r.room_id
        JOIN wing w ON r.wing_id = w.wing_id
        JOIN billing_account ba ON rr.billing_account_id = ba.account_id
        ORDER BY rr.reservation_id DESC LIMIT 35
    ''', {"today": today})
    guest_overview = cursor.fetchall()

    cursor.execute('''
        SELECT req.request_id, r.room_number, req.request_type, req.details, req.status 
        FROM room_request req
        JOIN room_reservation rr ON req.reservation_id = rr.reservation_id
        JOIN room r ON rr.room_id = r.room_id
        ORDER BY req.request_id DESC
    ''')
    all_requests = cursor.fetchall()

    cursor.execute('''
        WITH current_rooms AS (
            SELECT r.room_id, r.room_type_id,
                   CASE WHEN r.status = 'Clean/Vacant' AND EXISTS (
                       SELECT 1 FROM room_reservation rr
                       WHERE rr.room_id = r.room_id AND rr.reservation_status = 'Confirmed'
                         AND rr.check_in_date <= :today AND rr.check_out_date > :today
                   ) THEN 'Occupied' ELSE r.status END AS status
            FROM room r
        )
        SELECT rt.type_name, COUNT(r.room_id) AS total_rooms,
               SUM(r.status = 'Clean/Vacant') AS available_rooms,
               SUM(r.status = 'Occupied') AS occupied_rooms,
               ROUND(SUM(r.status = 'Occupied') * 100.0 / COUNT(r.room_id), 1) AS current_occupancy_rate
        FROM current_rooms r JOIN room_type rt ON r.room_type_id = rt.type_id
        GROUP BY rt.type_id, rt.type_name
    ''', {"today": today})
    room_availability = cursor.fetchall()

    cursor.execute(
        """SELECT COUNT(DISTINCT customer_id) FROM room_reservation
           WHERE reservation_status = 'Confirmed' AND check_in_date <= ? AND check_out_date > ?""",
        (today, today),
    )
    active_guests = cursor.fetchone()[0]
    vacant_rooms = sum(row["available_rooms"] for row in room_availability)
    cursor.execute("SELECT COUNT(*) FROM room_request WHERE status = 'Pending'")
    pending_requests = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM billing_account WHERE (total_charges - total_paid) > 0")
    unpaid_count = cursor.fetchone()[0]

    staff_stats = {'active_guests': active_guests, 'vacant_rooms': vacant_rooms, 'pending_requests': pending_requests, 'unpaid_count': unpaid_count}
    conn.close()
    return render_template('portal.html', view_mode='staff', guest_overview=guest_overview, all_requests=all_requests, room_availability=room_availability, staff_stats=staff_stats)

@app.route("/staff/update_request", methods=["POST"])
def staff_update_request():
    if session.get("role") not in ("staff", "manager"):
        return redirect(url_for("login_page", role="staff"))
    req_id = request.form.get("request_id", type=int)
    status = request.form.get("status")
    if req_id is None or status not in ("Pending", "In Progress", "Completed"):
        flash("Choose a valid request and status.")
        return redirect(url_for("staff_portal"))
    conn = get_db()
    cursor = conn.cursor()
    resolved_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'Completed' else None
    cursor.execute("UPDATE room_request SET status = ?, resolved_time = ? WHERE request_id = ?", (status, resolved_time, req_id))
    conn.commit()
    conn.close()
    flash(f"Work order #{req_id} updated to {status}.")
    return redirect(url_for('staff_portal'))

@app.route("/manager")
def manager_portal():
    if session.get('role') != 'manager':
        return redirect(url_for('login_page', role='manager'))

    period = request.args.get("period", "monthly")
    top_period = request.args.get("top_period", "yearly")
    conn = get_db()
    cursor = conn.cursor()

    if period == "weekly":
        cursor.execute("SELECT strftime('%Y-W%W', payment_time) AS time_unit, ROUND(SUM(amount), 2) AS total_revenue FROM payment WHERE payment_status = 'Success' GROUP BY time_unit ORDER BY time_unit ASC")
    elif period == "yearly":
        cursor.execute("SELECT strftime('%Y', payment_time) AS time_unit, ROUND(SUM(amount), 2) AS total_revenue FROM payment WHERE payment_status = 'Success' GROUP BY time_unit ORDER BY time_unit ASC")
    else:
        cursor.execute("SELECT strftime('%Y-%m', payment_time) AS time_unit, ROUND(SUM(amount), 2) AS total_revenue FROM payment WHERE payment_status = 'Success' GROUP BY time_unit ORDER BY time_unit ASC")

    trend_rows = cursor.fetchall()
    trend_labels = [r['time_unit'] for r in trend_rows]
    trend_values = [r['total_revenue'] for r in trend_rows]

    cursor.execute("SELECT item_category, ROUND(SUM(amount), 2) AS segment_revenue FROM billing_item GROUP BY item_category ORDER BY segment_revenue DESC")
    seg_rows = cursor.fetchall()
    segment_labels = [r['item_category'] for r in seg_rows]
    segment_values = [r['segment_revenue'] for r in seg_rows]

    if top_period == "monthly":
        cursor.execute('''
            SELECT u.full_name AS customer_name, c.organization_name,
                   COUNT(DISTINCT r.reservation_id) AS completed_room_stays,
                   ROUND(SUM(p.amount), 2) AS total_spent
            FROM customer c
            JOIN user u ON c.user_id = u.user_id
            JOIN billing_account ba ON c.customer_id = ba.customer_id
            JOIN payment p ON ba.account_id = p.account_id
            LEFT JOIN room_reservation r ON ba.account_id = r.billing_account_id
            WHERE p.payment_status = 'Success' AND strftime('%Y-%m', p.payment_time) = (SELECT strftime('%Y-%m', MAX(payment_time)) FROM payment)
            GROUP BY c.customer_id, u.full_name, c.organization_name
            ORDER BY total_spent DESC LIMIT 5
        ''')
    else:
        cursor.execute('''
            SELECT u.full_name AS customer_name, c.organization_name,
                   COUNT(DISTINCT r.reservation_id) AS completed_room_stays,
                   ROUND(SUM(p.amount), 2) AS total_spent
            FROM customer c
            JOIN user u ON c.user_id = u.user_id
            JOIN billing_account ba ON c.customer_id = ba.customer_id
            JOIN payment p ON ba.account_id = p.account_id
            LEFT JOIN room_reservation r ON ba.account_id = r.billing_account_id
            WHERE p.payment_status = 'Success'
            GROUP BY c.customer_id, u.full_name, c.organization_name
            ORDER BY total_spent DESC LIMIT 5
        ''')
    top_customers = cursor.fetchall()

    cursor.execute('''
        SELECT f.facility_name, f.facility_type, COUNT(ful.log_id) AS visit_count,
               ROUND(COUNT(ful.log_id) * 100.0 / (SELECT COUNT(*) FROM facility_usage_log), 1) AS usage_frequency_pct
        FROM facility f
        LEFT JOIN facility_usage_log ful ON f.facility_id = ful.facility_id
        GROUP BY f.facility_id, f.facility_name, f.facility_type
        ORDER BY visit_count DESC
    ''')
    facility_stats = cursor.fetchall()

    cursor.execute('''
        SELECT u.full_name AS staff_name, s.department, COUNT(sf.feedback_id) AS total_reviews,
               ROUND(AVG(sf.rating), 2) AS average_rating,
               SUM(CASE WHEN sf.rating >= 4 THEN 1 ELSE 0 END) AS positive_reviews
        FROM staff s
        JOIN user u ON s.user_id = u.user_id
        LEFT JOIN service_feedback sf ON s.staff_id = sf.staff_id
        GROUP BY s.staff_id, u.full_name, s.department
        HAVING total_reviews > 0 ORDER BY average_rating DESC
    ''')
    staff_reviews = cursor.fetchall()
    conn.close()

    return render_template('portal.html', view_mode='manager', period=period, top_period=top_period,
                                  trend_labels=trend_labels, trend_values=trend_values,
                                  segment_labels=segment_labels, segment_values=segment_values,
                                  top_customers=top_customers, facility_stats=facility_stats, staff_reviews=staff_reviews)

init_db()


if __name__ == "__main__":
    app.run(port=5000)
