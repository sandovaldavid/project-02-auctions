# **Auction Site**

## **Overview**

The Auction Site is a web application where users can create, bid on, and manage online auctions. It provides a platform for users to list items for sale, place competitive bids, and engage with the auction community through comments and watchlists.

The project is built using Django, leveraging its robust framework to manage user authentication, data modeling, and dynamic rendering of content.

---

## **Features**

### **User Authentication**
- Users can register, log in, and log out securely.
- Navigation dynamically adapts based on the user's authentication status.

### **Create Listings**
- Authenticated users can create auction listings with the following details:
  - Title
  - Description
  - Starting bid
  - Optional image URL
  - Optional category
- Listings are marked as active by default and can later be closed by the owner.

### **Active Listings Page**
- The homepage displays all currently active auctions.
- Each listing shows:
  - Title
  - Description
  - Current highest bid
  - Associated image (if provided)

### **Listing Page**
- Each listing has its own page displaying:
  - Full details of the listing
  - Current bid and bidding history
  - Comments from users
  - Buttons to add or remove the listing from the user's watchlist
- **Bid Functionality:**
  - Users can place bids that are higher than the current bid or the starting bid.
  - The page displays error messages if the bid does not meet these criteria.
- **Owner Controls:**
  - The creator of a listing can close the auction, making the highest bidder the winner.
- **Winner Notification:**
  - If a user wins an auction, the listing page will notify them.

### **Watchlist**
- Signed-in users can maintain a personalized watchlist of items they are interested in.
- Users can add or remove items from their watchlist with a single click.

### **Categories**
- Users can view all available categories of listings.
- Clicking on a category displays all active listings within that category.

### **Comments**
- Users can leave comments on any listing they view.
- All comments are displayed below the listing details.

### **Admin Interface**
- Site administrators can manage all listings, bids, and comments through Django’s admin panel.

---

## **Getting Started**

### **Prerequisites**
- Python 3.10 or higher
- Django 5.1.2 or higher

### **Setup Instructions**

1. **Clone the Repository**  
   ```bash
   git clone https://github.com/sandovaldavid/Project02_Commerce.git auction-site
   cd auction-site
   ```

2. **Install Dependencies**  
   Use a virtual environment for better dependency management.  
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Apply Migrations**  
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create a Superuser**  
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the Development Server**  
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**  
   Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## **Usage**

1. **Register and Log In**
   - Create an account or log in to access the site's functionality.
2. **Create Listings**
   - Use the "Create Listing" button to start a new auction.
3. **View and Bid**
   - Explore active listings, bid on items, or add them to your watchlist.
4. **Manage Listings**
   - Close your own listings or monitor their bidding activity.
5. **Engage with the Community**
   - Leave comments and interact with other users through bids and watchlists.

---

## **Project Structure**

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
├── static/             # CSS and JavaScript files
├── models.py           # Data models for the app
├── views.py            # Application logic and views
├── urls.py             # URL configuration
└── forms.py            # Django forms
```

---

## **Technologies Used**
- **Backend:** Django (Python)
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite (default)
- **Authentication:** Django's built-in authentication system

---

## **Future Improvements**
- Add real-time updates using WebSockets for live bidding.
- Implement advanced filtering options for listings (e.g., price range, categories).
- Include email notifications for bid updates and auction closures.
- Improve mobile responsiveness and UI/UX design.

---

## **License**

---
