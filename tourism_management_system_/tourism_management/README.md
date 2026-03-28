# 🌍 WanderLux — Tourism Management System
### Python Flask Web Application

---

## 📋 Project Overview

WanderLux is a full-featured **Tourism Management System** built with Python Flask and SQLite. It provides:
- A beautiful public-facing website for browsing destinations & packages
- User registration, login, and booking management
- Admin panel for managing destinations, bookings, and users

---

## ⚙️ Setup & Installation

### 1. Install Python
Make sure Python 3.8+ is installed:
```
python --version
```

### 2. Install Flask
```
pip install flask
```
Or using the requirements file:
```
pip install -r requirements.txt
```

### 3. Run the Application
```
python app.py
```

### 4. Open in Browser
```
http://localhost:5000
```

---

## 🔐 Demo Login Credentials

| Role  | Email                | Password   |
|-------|----------------------|------------|
| Admin | admin@tourism.com    | admin123   |
| User  | Register a new account |          |

---

## 📁 Project Structure

```
tourism_management/
├── app.py                  ← Main Flask application
├── requirements.txt        ← Python dependencies
├── database/
│   └── tourism.db          ← SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       ← Main stylesheet
│   └── js/
│       └── main.js         ← JavaScript
└── templates/
    ├── base.html           ← Base layout (navbar, footer)
    ├── index.html          ← Homepage
    ├── destinations.html   ← Destinations listing
    ├── destination_detail.html ← Single destination + booking
    ├── packages.html       ← Tour packages
    ├── book.html           ← Booking form
    ├── my_bookings.html    ← User bookings dashboard
    ├── profile.html        ← User profile
    ├── contact.html        ← Contact page
    ├── login.html          ← Login page
    ├── register.html       ← Register page
    └── admin/
        ├── base.html       ← Admin layout with sidebar
        ├── dashboard.html  ← Admin dashboard + stats
        ├── bookings.html   ← Manage all bookings
        ├── destinations.html ← Manage destinations
        ├── add_destination.html ← Add new destination
        └── users.html      ← View all users
```

---

## 🗄️ Database Schema

### users
| Column     | Type    | Description          |
|------------|---------|----------------------|
| id         | INTEGER | Primary key          |
| name       | TEXT    | Full name            |
| email      | TEXT    | Unique email         |
| password   | TEXT    | Password             |
| phone      | TEXT    | Phone number         |
| role       | TEXT    | 'user' or 'admin'    |
| created_at | TEXT    | Registration date    |

### destinations
| Column           | Type    | Description          |
|------------------|---------|----------------------|
| id               | INTEGER | Primary key          |
| name             | TEXT    | Destination name     |
| country          | TEXT    | Country              |
| city             | TEXT    | City                 |
| description      | TEXT    | Description          |
| category         | TEXT    | Beach/Adventure/etc  |
| image_url        | TEXT    | Image URL            |
| price_per_person | REAL    | Price in INR         |
| rating           | REAL    | Average rating       |
| max_capacity     | INTEGER | Max visitors         |
| available_slots  | INTEGER | Remaining slots      |

### bookings
| Column           | Type    | Description          |
|------------------|---------|----------------------|
| id               | INTEGER | Primary key          |
| user_id          | INTEGER | FK → users           |
| destination_id   | INTEGER | FK → destinations    |
| travel_date      | TEXT    | Departure date       |
| return_date      | TEXT    | Return date          |
| num_persons      | INTEGER | No. of travelers     |
| total_price      | REAL    | Total cost           |
| status           | TEXT    | pending/confirmed/cancelled |
| special_requests | TEXT    | Notes                |
| booking_date     | TEXT    | When booked          |

### reviews
| Column         | Type    | Description        |
|----------------|---------|--------------------|
| id             | INTEGER | Primary key        |
| user_id        | INTEGER | FK → users         |
| destination_id | INTEGER | FK → destinations  |
| rating         | INTEGER | 1–5 stars          |
| comment        | TEXT    | Review text        |
| created_at     | TEXT    | Date posted        |

### packages
| Column        | Type    | Description          |
|---------------|---------|----------------------|
| id            | INTEGER | Primary key          |
| name          | TEXT    | Package name         |
| description   | TEXT    | Description          |
| duration_days | INTEGER | Trip length          |
| price         | REAL    | Cost per person      |
| includes      | TEXT    | What's included      |
| destinations  | TEXT    | Covered cities       |
| image_url     | TEXT    | Image URL            |
| is_featured   | INTEGER | Show on homepage?    |

---

## ✨ Features

### Public Website
- 🏠 Beautiful homepage with hero video, stats, featured destinations & packages
- 🔍 Live search with instant suggestions
- 🗺️ Destinations page with category filters & text search
- 📄 Destination detail page with gallery, info & reviews
- 📦 Tour packages page
- 📞 Contact page

### User Features
- 🔐 User registration & login
- 📅 Book destinations with date selection & person count
- 💰 Dynamic price calculation
- 📋 View & cancel bookings
- ⭐ Write reviews with star ratings
- 👤 User profile page

### Admin Panel
- 📊 Dashboard with live statistics (revenue, bookings, users)
- ✅ Confirm or cancel bookings
- ➕ Add new destinations
- 🗑️ Delete destinations
- 👥 View all registered users

---

## 🛠️ Technologies Used

| Technology | Usage              |
|------------|--------------------|
| Python 3   | Backend language   |
| Flask      | Web framework      |
| SQLite     | Database           |
| Jinja2     | HTML templating    |
| HTML/CSS   | Frontend           |
| JavaScript | Interactivity      |
| Font Awesome | Icons            |
| Google Fonts | Typography       |

---

## 📌 Notes for Submission

- No external database setup needed — SQLite file is auto-created
- Sample data (destinations, packages, admin user) is auto-seeded on first run
- All CSS is custom-written (no Bootstrap dependency)
- Responsive design works on mobile and desktop

---

*Developed as a Python Web Development Project — Tourism Management System*
