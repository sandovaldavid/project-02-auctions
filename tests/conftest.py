import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from rest_framework.test import APIClient
import factory
from factory.django import DjangoModelFactory
from auctions.models import Listing, Bid, Comment
from decimal import Decimal

User = get_user_model()


# Factories for test data generation
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class ListingFactory(DjangoModelFactory):
    class Meta:
        model = Listing

    title = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("text", max_nb_chars=500)
    starting_bid = factory.Faker(
        "pydecimal", left_digits=3, right_digits=2, positive=True
    )
    category = factory.Faker(
        "random_element", elements=["Electronics", "Fashion", "Home", "Sports", "Books"]
    )
    user = factory.SubFactory(UserFactory)
    active = True


class BidFactory(DjangoModelFactory):
    class Meta:
        model = Bid

    amount = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)


class CommentFactory(DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Faker("text", max_nb_chars=200)
    user = factory.SubFactory(UserFactory)
    listing = factory.SubFactory(ListingFactory)


# Pytest fixtures
@pytest.fixture
def user():
    """Create a test user"""
    return UserFactory()


@pytest.fixture
def admin_user():
    """Create an admin user"""
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def listing(user):
    """Create a test listing"""
    return ListingFactory(user=user)


@pytest.fixture
def multiple_listings(user):
    """Create multiple test listings"""
    return ListingFactory.create_batch(5, user=user)


@pytest.fixture
def bid(user, listing):
    """Create a test bid"""
    return BidFactory(
        user=user, listing=listing, amount=listing.starting_bid + Decimal("10.00")
    )


@pytest.fixture
def comment(user, listing):
    """Create a test comment"""
    return CommentFactory(user=user, listing=listing)


@pytest.fixture
def client():
    """Django test client"""
    return Client()


@pytest.fixture
def api_client():
    """DRF API test client"""
    return APIClient()


@pytest.fixture
def authenticated_client(client, user):
    """Authenticated Django test client"""
    client.force_login(user)
    return client


@pytest.fixture
def authenticated_api_client(api_client, user):
    """Authenticated DRF API test client"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def sample_data(db):
    """Create sample data for testing"""
    users = UserFactory.create_batch(3)
    listings = []

    for user in users:
        user_listings = ListingFactory.create_batch(2, user=user)
        listings.extend(user_listings)

    # Create some bids
    for listing in listings[:3]:
        BidFactory.create_batch(2, listing=listing)

    # Create some comments
    for listing in listings[:2]:
        CommentFactory.create_batch(3, listing=listing)

    return {"users": users, "listings": listings}


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests"""
    pass
