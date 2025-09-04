import django
from auctions.models import User, Listing, Bid

django.setup()

# Get or create a user
user = User.objects.first()
if not user:
    user = User.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )

# Create test listing
listing = Listing.objects.create(
    title="Subasta de prueba",
    description="Descripción de prueba para mostrar fechas",
    starting_bid=100.00,
    user=user,
    category="Electronics",
)

# Create test bid
bid = Bid.objects.create(user=user, listing=listing, amount=150.00)

print("Datos de prueba creados exitosamente")
print(f"Listing creado: {listing.title} - {listing.created}")
print(f"Bid creado: {bid.amount} - {bid.created_at}")
print(f"Total listings: {Listing.objects.count()}")
print(f"Total bids: {Bid.objects.count()}")
