AnixCartx Backend

AnixCartx Backend is the server-side application powering the AnixCart e-commerce platform. It handles user authentication, product management, cart operations, order processing, and payment integration through secure REST APIs.

🚀 Features
User Authentication & Authorization
JWT / Token-Based Secure Login System
Product Management APIs
Category-Based Product Filtering
Cart Management APIs
Order Placement & Checkout Handling
Cash on Delivery (COD) Support
Admin Panel for Product & Order Management
RESTful API Architecture
🛠 Tech Stack
Backend Framework: Django
API Framework: Django REST Framework
Database: SQLite 
Authentication: JWT / Token Authentication
Deployment: Render 
📂 Installation
git clone
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
🔐 Authentication Endpoints
Register User
Login User
Logout User
JWT Token Refresh (if used)
🛒 Core APIs
Product Listing API
Category Filter API
Cart Add / Remove API
Checkout API
🧑‍💼 Admin Features
Manage Products
Manage Categories
Track Orders
Update Order Status
📌 Future Enhancements
Wishlist API

👨‍💻 Author

Anish Prajapti
