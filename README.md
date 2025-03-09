# 🛒 Auction Site

[![Django](https://img.shields.io/badge/Django-5.1.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Mobile Responsive](https://img.shields.io/badge/Mobile-Responsive-orange.svg)](https://getbootstrap.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📋 Overview

Auction Site is a comprehensive web application that enables users to participate in online auctions. Built with Django, the platform provides a seamless experience for creating auction listings, placing competitive bids, and engaging with other users through comments and watchlists. The application features a responsive design that works across desktop and mobile devices, with carefully crafted UI components and a modern user experience.

## ✨ Live Demo

🔗 [View Live Demo](https://auction-site-demo.herokuapp.com) (Replace with your actual deployment URL)

## 📱 Screenshots

### Desktop View

![Desktop View](/assets/desktop-edmo.png)

### Mobile View

![Mobile View](/assets/mobile-demo.png)

## 🚀 Features

### 🔐 User Authentication

-   Secure registration, login, and logout functionality
-   Dynamic navigation based on authentication status
-   User profile management
-   Password protection and security measures

### 📝 Listing Management

-   Create detailed auction listings with:
    -   Title and description
    -   Starting bid amount
    -   Optional image URL
    -   Optional category selection
-   Active/inactive listing status control
-   Intuitive forms with validation

### 🏠 Active Listings Page

-   Browse all currently active auctions
-   View essential listing details at a glance
-   Filter listings by categories
-   Responsive card layout for all device sizes

### 📊 Detailed Listing Pages

-   Comprehensive listing information display
-   Current bid and bidding history
-   User comments section
-   Watchlist management buttons
-   Bidding functionality with validation
-   Auction closing mechanism for listing owners
-   Winner notifications

### ⭐ Watchlist

-   Personalized collection of interesting items
-   One-click add/remove functionality
-   Quick access to watched items
-   Visual indicators for watched items

### 🏷️ Categories

-   Organized listing categories
-   Filter listings by specific categories
-   Browse all available categories
-   Category-specific pages

### 💬 Comments

-   Leave comments on any listing
-   View all comments on listings
-   Community interaction
-   Timestamp and author information

### ⚙️ Admin Interface

-   Comprehensive management dashboard
-   Control over all listings, bids, and comments
-   User management capabilities
-   Data filtering and search functionality

## 🛠️ Technologies Used

-   **Backend**: [Django](https://www.djangoproject.com/) (Python) - Robust web framework
-   **Frontend**: HTML, CSS, [Bootstrap](https://getbootstrap.com/) - Responsive design
-   **Database**: SQLite (development), PostgreSQL (production-ready)
-   **Authentication**: Django's built-in authentication system
-   **Styling**: Custom CSS with responsive design, Font Awesome icons
-   **Deployment**: Docker container support
-   **Version Control**: Git
-   **Responsive Design**: Media queries and Bootstrap grid system
-   **UI Components**: Custom cards, navigation, forms, and alerts

## 🔧 Installation & Setup

### Prerequisites

-   Python 3.10 or higher
-   Django 5.1.2 or higher
-   Required system packages (Ubuntu):

```bash
sudo apt update
sudo apt install build-essential libpq-dev python3-dev
```

### Local Setup

1. **Clone the Repository**

```bash
git clone https://github.com/sandovaldavid/project-02-auctions.git
cd auction-site
```

2. **Install Dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Apply Database Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Create Admin User**

```bash
python manage.py createsuperuser
```

5. **Run Development Server**

```bash
python manage.py runserver
```

6. **Access the Application**  
   Open [http://localhost:8000](http://localhost:8000) in your browser

### Docker Setup

1. **Build and Run with Docker Compose**

```bash
docker compose up --build
```

2. **Access the Application**  
   Open [http://localhost:8000](http://localhost:8000) in your browser

## 📂 Project Structure

```plaintext
auctions/
├── migrations/         # Database migration files
├── templates/          # HTML templates for the app
│   ├── auctions/
│   │   ├── layout.html         # Base layout
│   │   ├── index.html          # Active listings page
│   │   ├── create.html         # Create listing page
│   │   ├── listing.html        # Listing details page
│   │   ├── categories.html     # Categories page
│   │   └── watchlist.html      # Watchlist page
│   └── auctions/components/    # Reusable UI components
│       ├── footer.html         # Site footer
│       └── ...                 # Other components
├── static/             # CSS and JavaScript files
│   ├── css/
│   │   ├── auctions/           # Page-specific styles
│   │   ├── components/         # Component styles
│   │   └── styles.css          # Base styles
│   └── js/                     # JavaScript files
├── models.py           # Data models for the app
├── views.py            # Application logic and views
├── urls.py             # URL configuration
├── forms.py            # Django forms
├── context_processors.py # Custom context processors
└── admin.py            # Admin interface configuration
```

## 📱 Usage Guide

1. **Register and Sign In**

    - Create a new account or log in to access full functionality
    - Navigate through the responsive interface

2. **Browse Listings**

    - Explore the homepage for all active auctions
    - Use category filters to find specific items

3. **Create Your Own Listing**

    - Click "Create Listing" in the navigation menu
    - Fill out the form with your item's details
    - Publish your auction

4. **Bidding**

    - Place bids on active listings
    - Monitor your active bids
    - Receive notifications if you win an auction

5. **Manage Watchlist**

    - Add interesting items to your watchlist
    - Remove items as needed
    - Quick access to your watched items

6. **Interact with Community**
    - Leave comments on listings
    - Engage with sellers and other bidders

## 🎨 UI/UX Features

-   **Responsive Design**: Optimized for all screen sizes from mobile to desktop
-   **Dark/Light Mode**: Support for system theme preferences
-   **Accessibility**: Focus states and semantic HTML
-   **Modern Interface**: Clean design with consistent spacing and typography
-   **Intuitive Navigation**: Clear user paths through the application
-   **Microinteractions**: Visual feedback for user actions

## 🔄 API Endpoints

The application doesn't currently expose public APIs but uses Django's URL routing for all functionality.

## 🔒 Security Features

-   CSRF protection for all forms
-   Password hashing and secure authentication
-   Form validation to prevent malicious inputs
-   Django's security middleware configuration

## 🚧 Future Improvements

-   Real-time updates using WebSockets for live bidding experiences
-   Advanced listing filtering options (price range, date listed)
-   Email notification system for bid updates and auction closures
-   Enhanced mobile responsiveness and UI/UX improvements
-   Payment gateway integration for completed auctions
-   User ratings and reviews system
-   Enhanced search functionality with autocomplete
-   Social media sharing integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🧪 Testing

Run the test suite to ensure everything is working correctly:

```bash
python manage.py test
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

David Sandoval - [@sandovaldavid](https://github.com/sandovaldavid)

Project Link: [https://github.com/sandovaldavid/project-02-auctions.git](https://github.com/sandovaldavid/project-02-auctions.git)
