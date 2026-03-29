from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3
import os
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'tourism_secret_key_2024'

DB_PATH = 'database/tourism.db'

# ─── DATABASE SETUP ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        role TEXT DEFAULT 'user',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        description TEXT,
        category TEXT,
        image_url TEXT,
        price_per_person REAL DEFAULT 0,
        rating REAL DEFAULT 0,
        max_capacity INTEGER DEFAULT 50,
        available_slots INTEGER DEFAULT 50,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        destination_id INTEGER,
        travel_date TEXT NOT NULL,
        return_date TEXT,
        num_persons INTEGER DEFAULT 1,
        total_price REAL,
        status TEXT DEFAULT 'pending',
        special_requests TEXT,
        booking_date TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(destination_id) REFERENCES destinations(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS reviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        destination_id INTEGER,
        rating INTEGER,
        comment TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(destination_id) REFERENCES destinations(id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS packages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        duration_days INTEGER,
        price REAL,
        includes TEXT,
        destinations TEXT,
        image_url TEXT,
        is_featured INTEGER DEFAULT 0
    )''')

    # Seed admin user
    c.execute("SELECT id FROM users WHERE email='admin@tourism.com'")
    if not c.fetchone():
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                  ('Admin', 'admin@tourism.com', 'admin123', 'admin'))

    # Seed sample destinations
    c.execute("SELECT COUNT(*) FROM destinations")
    if c.fetchone()[0] == 0:
        destinations = [
            ('Taj Mahal', 'India', 'Agra', 'One of the Seven Wonders of the World. A stunning white marble mausoleum.', 'Heritage', 'https://images.unsplash.com/photo-1564507592333-c60657eea523?w=800', 4500, 4.9, 200, 150),
            ('Goa Beaches', 'India', 'Goa', 'Beautiful sandy beaches, vibrant nightlife, and Portuguese heritage.', 'Beach', 'https://images.unsplash.com/photo-1614082242765-7c98ca0f3df3?w=800', 3200, 4.7, 300, 220),
            ('Kerala Backwaters', 'India', 'Alleppey', 'Serene houseboat cruises through lush green backwaters and lagoons.', 'Nature', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800', 5500, 4.8, 100, 80),
            ('Rajasthan Desert', 'India', 'Jaisalmer', 'Golden sand dunes, camel safaris and majestic forts of the Thar Desert.', 'Adventure', 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=800', 6000, 4.6, 150, 120),
            ('Manali Hills', 'India', 'Manali', 'Snow-capped peaks, adventure sports and scenic Himalayan beauty.', 'Adventure', 'https://images.unsplash.com/photo-1626621341517-bbf3d9990a23?w=800', 7000, 4.8, 80, 60),
            ('Andaman Islands', 'India', 'Port Blair', 'Crystal clear water, coral reefs and pristine white sand beaches.', 'Beach', 'https://images.unsplash.com/photo-1559494007-9f5847c49d94?w=800', 9500, 4.9, 60, 45),
        ]
        c.executemany('''INSERT INTO destinations 
            (name, country, city, description, category, image_url, price_per_person, rating, max_capacity, available_slots)
            VALUES (?,?,?,?,?,?,?,?,?,?)''', destinations)

    # Seed packages
    c.execute("SELECT COUNT(*) FROM packages")
    if c.fetchone()[0] == 0:
        packages = [
            ('Golden Triangle', 'Delhi, Agra & Jaipur — India\'s most iconic triangle tour', 7, 18500, 'Hotel stays, Breakfast, Guide, Transport, Entry Fees', 'Delhi, Agra, Jaipur', 'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800', 1),
            ('Beach Paradise', 'Goa + Andaman island hopping package', 10, 28000, 'Resorts, All Meals, Water Sports, Ferry, Flights', 'Goa, Andaman', 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800', 1),
            ('Himalayan Adventure', 'Manali to Leh bike/road trip experience', 12, 35000, 'Camping, All Meals, Bike Rental, Guide, Permits', 'Manali, Leh', 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800', 1),
            ('Kerala Bliss', 'Backwaters, hills and beaches of God\'s Own Country', 8, 22000, 'Houseboat, Resorts, Breakfast, Ayurvedic Spa, Transport', 'Alleppey, Munnar, Kovalam', 'https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=800', 0),
        ]
        c.executemany('''INSERT INTO packages (name, description, duration_days, price, includes, destinations, image_url, is_featured)
            VALUES (?,?,?,?,?,?,?,?)''', packages)

    conn.commit()
    conn.close()

# ─── AUTH HELPERS ─────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

# ─── PUBLIC ROUTES ────────────────────────────────────────────────────────────

@app.route('/')
def index():
    conn = get_db()
    destinations = conn.execute('SELECT * FROM destinations ORDER BY rating DESC LIMIT 6').fetchall()
    packages = conn.execute('SELECT * FROM packages WHERE is_featured=1').fetchall()
    stats = {
        'destinations': conn.execute('SELECT COUNT(*) FROM destinations').fetchone()[0],
        'bookings': conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0],
        'users': conn.execute('SELECT COUNT(*) FROM users WHERE role="user"').fetchone()[0],
        'packages': conn.execute('SELECT COUNT(*) FROM packages').fetchone()[0],
    }
    conn.close()
    return render_template('index.html', destinations=destinations, packages=packages, stats=stats)

@app.route('/destinations')
def destinations():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    conn = get_db()
    query = 'SELECT * FROM destinations WHERE 1=1'
    params = []
    if category:
        query += ' AND category=?'
        params.append(category)
    if search:
        query += ' AND (name LIKE ? OR city LIKE ? OR country LIKE ?)'
        params += [f'%{search}%', f'%{search}%', f'%{search}%']
    query += ' ORDER BY rating DESC'
    dests = conn.execute(query, params).fetchall()
    categories = conn.execute('SELECT DISTINCT category FROM destinations').fetchall()
    conn.close()
    return render_template('destinations.html', destinations=dests, categories=categories,
                           selected_category=category, search=search)

@app.route('/destination/<int:dest_id>')
def destination_detail(dest_id):
    conn = get_db()
    dest = conn.execute('SELECT * FROM destinations WHERE id=?', (dest_id,)).fetchone()
    reviews = conn.execute('''SELECT r.*, u.name as user_name 
        FROM reviews r JOIN users u ON r.user_id=u.id 
        WHERE r.destination_id=? ORDER BY r.created_at DESC''', (dest_id,)).fetchall()
    conn.close()
    if not dest:
        flash('Destination not found.', 'danger')
        return redirect(url_for('destinations'))
    return render_template('destination_detail.html', dest=dest, reviews=reviews)

@app.route('/packages')
def packages():
    conn = get_db()
    pkgs = conn.execute('SELECT * FROM packages ORDER BY is_featured DESC').fetchall()
    conn.close()
    return render_template('packages.html', packages=pkgs)

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ─── AUTH ROUTES ──────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (name, email, password, phone) VALUES (?,?,?,?)',
                         (name, email, password, phone))
            conn.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['role'] = user['role']
            flash(f'Welcome back, {user["name"]}!', 'success')
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('index'))

# ─── USER ROUTES ──────────────────────────────────────────────────────────────

@app.route('/book/<int:dest_id>', methods=['GET', 'POST'])
@login_required
def book(dest_id):
    conn = get_db()
    dest = conn.execute('SELECT * FROM destinations WHERE id=?', (dest_id,)).fetchone()
    if request.method == 'POST':
        travel_date = request.form['travel_date']
        return_date = request.form['return_date']
        num_persons = int(request.form['num_persons'])
        special_requests = request.form.get('special_requests', '')
        total_price = dest['price_per_person'] * num_persons
        conn.execute('''INSERT INTO bookings 
            (user_id, destination_id, travel_date, return_date, num_persons, total_price, special_requests)
            VALUES (?,?,?,?,?,?,?)''',
            (session['user_id'], dest_id, travel_date, return_date, num_persons, total_price, special_requests))
        conn.execute('UPDATE destinations SET available_slots=available_slots-? WHERE id=?', (num_persons, dest_id))
        conn.commit()
        conn.close()
        flash('Booking confirmed! Check your bookings for details.', 'success')
        return redirect(url_for('my_bookings'))
    conn.close()
    return render_template('book.html', dest=dest, today=date.today().isoformat())

@app.route('/my-bookings')
@login_required
def my_bookings():
    conn = get_db()
    bookings = conn.execute('''SELECT b.*, d.name as dest_name, d.city, d.country, d.image_url
        FROM bookings b JOIN destinations d ON b.destination_id=d.id
        WHERE b.user_id=? ORDER BY b.booking_date DESC''', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('my_bookings.html', bookings=bookings)

@app.route('/cancel-booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    conn = get_db()
    booking = conn.execute('SELECT * FROM bookings WHERE id=? AND user_id=?',
                           (booking_id, session['user_id'])).fetchone()
    if booking:
        conn.execute("UPDATE bookings SET status='cancelled' WHERE id=?", (booking_id,))
        conn.execute('UPDATE destinations SET available_slots=available_slots+? WHERE id=?',
                     (booking['num_persons'], booking['destination_id']))
        conn.commit()
        flash('Booking cancelled successfully.', 'info')
    conn.close()
    return redirect(url_for('my_bookings'))

@app.route('/add-review/<int:dest_id>', methods=['POST'])
@login_required
def add_review(dest_id):
    rating = int(request.form['rating'])
    comment = request.form['comment']
    conn = get_db()
    conn.execute('INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?,?,?,?)',
                 (session['user_id'], dest_id, rating, comment))
    avg = conn.execute('SELECT AVG(rating) FROM reviews WHERE destination_id=?', (dest_id,)).fetchone()[0]
    conn.execute('UPDATE destinations SET rating=? WHERE id=?', (round(avg, 1), dest_id))
    conn.commit()
    conn.close()
    flash('Review added! Thank you.', 'success')
    return redirect(url_for('destination_detail', dest_id=dest_id))

@app.route('/profile')
@login_required
def profile():
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    total_bookings = conn.execute('SELECT COUNT(*) FROM bookings WHERE user_id=?', (session['user_id'],)).fetchone()[0]
    conn.close()
    return render_template('profile.html', user=user, total_bookings=total_bookings)

# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    conn = get_db()
    stats = {
        'total_users': conn.execute('SELECT COUNT(*) FROM users WHERE role="user"').fetchone()[0],
        'total_bookings': conn.execute('SELECT COUNT(*) FROM bookings').fetchone()[0],
        'pending_bookings': conn.execute("SELECT COUNT(*) FROM bookings WHERE status='pending'").fetchone()[0],
        'confirmed_bookings': conn.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'total_revenue': conn.execute("SELECT SUM(total_price) FROM bookings WHERE status!='cancelled'").fetchone()[0] or 0,
        'total_destinations': conn.execute('SELECT COUNT(*) FROM destinations').fetchone()[0],
    }
    recent_bookings = conn.execute('''SELECT b.*, u.name as user_name, d.name as dest_name
        FROM bookings b JOIN users u ON b.user_id=u.id JOIN destinations d ON b.destination_id=d.id
        ORDER BY b.booking_date DESC LIMIT 10''').fetchall()
    conn.close()
    return render_template('admin/dashboard.html', stats=stats, recent_bookings=recent_bookings)

@app.route('/admin/bookings')
@login_required
@admin_required
def admin_bookings():
    conn = get_db()
    bookings = conn.execute('''SELECT b.*, u.name as user_name, u.email, d.name as dest_name
        FROM bookings b JOIN users u ON b.user_id=u.id JOIN destinations d ON b.destination_id=d.id
        ORDER BY b.booking_date DESC''').fetchall()
    conn.close()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/update-booking/<int:booking_id>/<status>')
@login_required
@admin_required
def update_booking_status(booking_id, status):
    conn = get_db()
    conn.execute('UPDATE bookings SET status=? WHERE id=?', (status, booking_id))
    conn.commit()
    conn.close()
    flash(f'Booking #{booking_id} updated to {status}.', 'success')
    return redirect(url_for('admin_bookings'))

@app.route('/admin/destinations')
@login_required
@admin_required
def admin_destinations():
    conn = get_db()
    dests = conn.execute('SELECT * FROM destinations ORDER BY id DESC').fetchall()
    conn.close()
    return render_template('admin/destinations.html', destinations=dests)

@app.route('/admin/add-destination', methods=['GET', 'POST'])
@login_required
@admin_required
def add_destination():
    if request.method == 'POST':
        data = (request.form['name'], request.form['country'], request.form['city'],
                request.form['description'], request.form['category'], request.form['image_url'],
                float(request.form['price']), int(request.form['capacity']))
        conn = get_db()
        conn.execute('''INSERT INTO destinations 
            (name, country, city, description, category, image_url, price_per_person, max_capacity, available_slots)
            VALUES (?,?,?,?,?,?,?,?,?)''', data + (data[7],))
        conn.commit()
        conn.close()
        flash('Destination added successfully!', 'success')
        return redirect(url_for('admin_destinations'))
    return render_template('admin/add_destination.html')

@app.route('/admin/delete-destination/<int:dest_id>')
@login_required
@admin_required
def delete_destination(dest_id):
    conn = get_db()
    conn.execute('DELETE FROM destinations WHERE id=?', (dest_id,))
    conn.commit()
    conn.close()
    flash('Destination deleted.', 'info')
    return redirect(url_for('admin_destinations'))

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    conn = get_db()
    users = conn.execute('''SELECT u.*, COUNT(b.id) as booking_count 
        FROM users u LEFT JOIN bookings b ON u.id=b.user_id 
        GROUP BY u.id ORDER BY u.created_at DESC''').fetchall()
    conn.close()
    return render_template('admin/users.html', users=users)

# ─── API ──────────────────────────────────────────────────────────────────────

@app.route('/api/search')
def api_search():
    q = request.args.get('q', '')
    conn = get_db()
    results = conn.execute('''SELECT id, name, city, country, category, price_per_person 
        FROM destinations WHERE name LIKE ? OR city LIKE ? LIMIT 5''',
        (f'%{q}%', f'%{q}%')).fetchall()
    conn.close()
    return jsonify([dict(r) for r in results])

if __name__ == '__main__':
    os.makedirs('database', exist_ok=True)
    init_db()
    app.run(debug=True, port=5000)
