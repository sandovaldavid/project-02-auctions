#!/usr/bin/env python
"""
Script de gestión de datos para el proyecto de subastas.
Uso: python manage_data.py [comando]

Comandos disponibles:
- load: Cargar datos de prueba
- clear: Limpiar todos los datos
- reset: Limpiar y cargar datos de prueba
- stats: Mostrar estadísticas de la base de datos
"""

import os
import sys
import django
from decimal import Decimal

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commerce.settings")
django.setup()

# Imports después de django.setup()
from auctions.models import User, Listing, Bid, Comment, Watchlist  # noqa: E402


def clear_data():
    """Limpiar todos los datos de prueba"""
    print("🧹 Limpiando datos...")

    # Contar antes de limpiar
    counts_before = {
        "watchlist": Watchlist.objects.count(),
        "comments": Comment.objects.count(),
        "bids": Bid.objects.count(),
        "listings": Listing.objects.count(),
        "users": User.objects.filter(is_superuser=False).count(),
    }

    # Limpiar en orden
    Watchlist.objects.all().delete()
    Comment.objects.all().delete()
    Bid.objects.all().delete()
    Listing.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    print(
        f"   ✅ Eliminados: {counts_before['watchlist']} watchlist, {counts_before['comments']} comentarios"
    )
    print(
        f"   ✅ Eliminados: {counts_before['bids']} pujas, {counts_before['listings']} subastas"
    )
    print(
        f"   ✅ Eliminados: {counts_before['users']} usuarios (manteniendo superusuarios)"
    )
    print("🎉 Datos limpiados exitosamente!")


def show_stats():
    """Mostrar estadísticas de la base de datos"""
    print("📊 Estadísticas de la base de datos:")
    print(f"   👥 Usuarios totales: {User.objects.count()}")
    print(f"   👤 Superusuarios: {User.objects.filter(is_superuser=True).count()}")
    print(f"   🏷️ Subastas activas: {Listing.objects.filter(active=True).count()}")
    print(f"   🏷️ Subastas totales: {Listing.objects.count()}")
    print(f"   💰 Pujas totales: {Bid.objects.count()}")
    print(f"   💬 Comentarios: {Comment.objects.count()}")
    print(f"   ⭐ Items en watchlist: {Watchlist.objects.count()}")

    # Estadísticas por categoría
    categories = Listing.objects.values("category").distinct().count()
    print(f"   📈 Categorías únicas: {categories}")

    # Subastas con más pujas
    if Listing.objects.exists():
        top_listings = Listing.objects.all()[:3]
        print("\n🔥 Top 3 subastas:")
        for listing in top_listings:
            bid_count = Bid.objects.filter(listing=listing).count()
            print(
                f"   • {listing.title[:40]}... - {bid_count} pujas - ${listing.current_bid}"
            )

    # Usuarios más activos
    if User.objects.filter(is_superuser=False).exists():
        print("\n👑 Usuarios más activos:")
        users = User.objects.filter(is_superuser=False)[:3]
        for user in users:
            listings_count = Listing.objects.filter(user=user).count()
            bids_count = Bid.objects.filter(user=user).count()
            print(
                f"   • {user.username} - {listings_count} subastas, {bids_count} pujas"
            )


def load_sample_data():
    """Cargar datos de prueba básicos"""
    print("🚀 Cargando datos de prueba...")

    # Crear algunos usuarios
    users_data = [
        {
            "username": "demo_user1",
            "email": "demo1@example.com",
            "first_name": "Demo",
            "last_name": "User1",
        },
        {
            "username": "demo_user2",
            "email": "demo2@example.com",
            "first_name": "Demo",
            "last_name": "User2",
        },
        {
            "username": "demo_user3",
            "email": "demo3@example.com",
            "first_name": "Demo",
            "last_name": "User3",
        },
    ]

    users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"], defaults=user_data
        )
        if created:
            user.set_password("demo123")
            user.save()
            print(f"   ✅ Usuario creado: {user.username}")
        users.append(user)

    # Crear algunas subastas
    sample_listings = [
        {
            "title": "Smartphone Samsung Galaxy",
            "description": "Smartphone en excelente estado, incluye cargador.",
            "starting_bid": Decimal("300.00"),
            "category": "Electrónicos",
        },
        {
            "title": "Libro de Programación Python",
            "description": "Libro completo sobre programación en Python.",
            "starting_bid": Decimal("25.00"),
            "category": "Libros",
        },
        {
            "title": "Auriculares Bluetooth",
            "description": "Auriculares inalámbricos con cancelación de ruido.",
            "starting_bid": Decimal("80.00"),
            "category": "Electrónicos",
        },
    ]

    for i, listing_data in enumerate(sample_listings):
        listing = Listing.objects.create(
            title=listing_data["title"],
            description=listing_data["description"],
            starting_bid=listing_data["starting_bid"],
            current_bid=listing_data["starting_bid"],
            category=listing_data["category"],
            user=users[i % len(users)],
            active=True,
        )
        print(f"   ✅ Subasta creada: {listing.title}")

        # Agregar una puja a cada subasta
        if len(users) > 1:
            bidder = users[(i + 1) % len(users)]
            bid_amount = listing.starting_bid + Decimal("10.00")

            Bid.objects.create(listing=listing, user=bidder, amount=bid_amount)

            listing.current_bid = bid_amount
            listing.save()

            print(f"   ✅ Puja creada: ${bid_amount} por {bidder.username}")

    print("🎉 Datos de prueba básicos cargados!")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    command = sys.argv[1].lower()

    if command == "load":
        load_sample_data()
    elif command == "clear":
        clear_data()
    elif command == "reset":
        clear_data()
        print()
        load_sample_data()
    elif command == "stats":
        show_stats()
    else:
        print(f"❌ Comando desconocido: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
