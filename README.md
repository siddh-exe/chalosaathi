# 🚌 ChaloSaathi

ChaloSaathi is a web-based travel assistance and ride-booking platform built using **Django**, **Leaflet**, and **OpenStreetMap**.  
It helps users easily search, book, and manage rides while providing an interactive map experience for navigation and live location tracking.

---

## 📋 Table of Contents
- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Project](#running-the-project)
- [Folder Structure](#folder-structure)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## 🧐 About

**ChaloSaathi** aims to make local travel easy and reliable.  
It allows users to:
- Book rides with nearby drivers.
- View routes and locations in real-time using OpenStreetMap.
- Get estimated distances and durations via **Geopy**.
- Handle background tasks like notifications and ride status updates using **Celery**.

---

## ✨ Features
- 🔐 User Authentication (Sign-up, Login, Logout)
- 🗺️ Interactive map using **Leaflet + OpenStreetMap**
- 📍 Real-time location tracking
- 🚖 Ride booking and management
- 📬 Background task handling with **Celery**
- 🧭 Distance and route calculations via **Geopy**
- 💬 Email/notification task support

---

## 🛠️ Tech Stack

**Frontend**
- HTML5  
- CSS3  
- JavaScript  
- Leaflet (OpenStreetMap Integration)

**Backend**
- Python  
- Django Framework  
- Celery (for background tasks)  
- Geopy (for geolocation and distance)

**Database**
- MySql

---

## ⚙️ Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/siddh-exe/chalosaathi.git
cd chalosaathi
```

### 3️⃣ Install Dependencies

```bash
pip install django celery geopy pillow
```

---

## ▶️ Running the Project

### Step 1: Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Start Celery Worker
```bash
celery -A chalosaathi worker -l info
```

### Step 3: Run the Django Development Server
```bash
python manage.py runserver
```

Now open your browser and visit:  
👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/index/)

---
