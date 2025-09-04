#!/usr/bin/env python
"""
Script para cargar datos de prueba en el proyecto de subastas.
Ejecuta: python manage.py shell < load_test_data.py
"""

import os
import django
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "commerce.settings")
django.setup()

# Imports después de django.setup()
from auctions.models import User, Listing, Bid, Comment, Watchlist  # noqa: E402


def create_test_data():
    print("🚀 Iniciando carga de datos de prueba...")

    # Limpiar datos existentes (opcional)
    print("🧹 Limpiando datos existentes...")
    Watchlist.objects.all().delete()
    Comment.objects.all().delete()
    Bid.objects.all().delete()
    Listing.objects.all().delete()
    User.objects.filter(is_superuser=False).delete()

    # Crear usuarios de prueba
    print("👥 Creando usuarios...")
    users = []

    # Usuario administrador (si no existe)
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@example.com",
            "first_name": "Admin",
            "last_name": "User",
            "is_staff": True,
            "is_superuser": True,
        },
    )
    if created:
        admin_user.set_password("admin123")
        admin_user.save()
        print(f"   ✅ Administrador creado: {admin_user.username}")

    # Usuarios regulares
    user_data = [
        {
            "username": "juan_perez",
            "email": "juan@example.com",
            "first_name": "Juan",
            "last_name": "Pérez",
        },
        {
            "username": "maria_garcia",
            "email": "maria@example.com",
            "first_name": "María",
            "last_name": "García",
        },
        {
            "username": "carlos_lopez",
            "email": "carlos@example.com",
            "first_name": "Carlos",
            "last_name": "López",
        },
        {
            "username": "ana_martinez",
            "email": "ana@example.com",
            "first_name": "Ana",
            "last_name": "Martínez",
        },
        {
            "username": "luis_rodriguez",
            "email": "luis@example.com",
            "first_name": "Luis",
            "last_name": "Rodríguez",
        },
        {
            "username": "sofia_hernandez",
            "email": "sofia@example.com",
            "first_name": "Sofía",
            "last_name": "Hernández",
        },
    ]

    for user_info in user_data:
        user, created = User.objects.get_or_create(
            username=user_info["username"], defaults=user_info
        )
        if created:
            user.set_password("password123")
            user.save()
            print(f"   ✅ Usuario creado: {user.username}")
        users.append(user)

    # Crear subastas de prueba
    print("🏷️ Creando subastas...")
    listings_data = [
        {
            "title": "iPhone 14 Pro Max 256GB",
            "description": "iPhone 14 Pro Max en excelente estado, color morado, 256GB de almacenamiento. Incluye cargador original y caja.",
            "starting_bid": Decimal("800.00"),
            "category": "Electrónicos",
            "image": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400",
        },
        {
            "title": "Laptop Gaming ASUS ROG",
            "description": "Laptop gaming ASUS ROG Strix con RTX 3070, Intel i7, 16GB RAM, SSD 1TB. Perfecta para gaming y trabajo.",
            "starting_bid": Decimal("1200.00"),
            "category": "Electrónicos",
            "image": "https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=400",
        },
        {
            "title": "Reloj Rolex Submariner",
            "description": "Reloj Rolex Submariner auténtico, modelo clásico en acero inoxidable. Certificado de autenticidad incluido.",
            "starting_bid": Decimal("5000.00"),
            "category": "Joyería",
            "image": "https://images.unsplash.com/photo-1547996160-81dfa63595aa?w=400",
        },
        {
            "title": "Bicicleta de Montaña Trek",
            "description": "Bicicleta de montaña Trek en excelente estado, suspensión completa, cambios Shimano, ideal para trails.",
            "starting_bid": Decimal("450.00"),
            "category": "Deportes",
            "image": "https://th.bing.com/th/id/R.214b6f959893ff7bc6650cb4418fa363?rik=0t4TBSfJrJX6vQ&pid=ImgRaw&r=0",
        },
        {
            "title": "Guitarra Eléctrica Fender",
            "description": "Guitarra eléctrica Fender Stratocaster americana, color sunburst, con estuche rígido incluido.",
            "starting_bid": Decimal("800.00"),
            "category": "Música",
            "image": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=400",
        },
        {
            "title": "Cámara Canon EOS R5",
            "description": "Cámara profesional Canon EOS R5 con lente 24-70mm f/2.8, perfecta para fotografía profesional.",
            "starting_bid": Decimal("2500.00"),
            "category": "Fotografía",
            "image": "https://images.unsplash.com/photo-1606983340126-99ab4feaa64a?w=400",
        },
        {
            "title": "Sofá de Cuero Italiano",
            "description": "Sofá de 3 plazas en cuero italiano genuino, color marrón, muy cómodo y en excelente estado.",
            "starting_bid": Decimal("600.00"),
            "category": "Hogar",
            "image": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=400",
        },
        {
            "title": "Zapatillas Nike Air Jordan",
            "description": "Zapatillas Nike Air Jordan 1 Retro High, edición limitada, talla 42, nuevas en caja.",
            "starting_bid": Decimal("200.00"),
            "category": "Moda",
            "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400",
        },
        {
            "title": "Libro Colección Harry Potter",
            "description": "Colección completa de libros de Harry Potter, edición de tapa dura, en perfecto estado.",
            "starting_bid": Decimal("80.00"),
            "category": "Libros",
            "image": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400",
        },
        {
            "title": "Consola PlayStation 5",
            "description": "PlayStation 5 nueva, incluye control DualSense y juego Spider-Man Miles Morales.",
            "starting_bid": Decimal("500.00"),
            "category": "Videojuegos",
            "image": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=400",
        },
    ]

    listings = []
    for i, listing_data in enumerate(listings_data):
        # Crear fechas variadas en los últimos 3 meses
        days_ago = (i * 7) % 90  # Distribuir en 90 días
        created_date = timezone.now() - timedelta(days=days_ago)

        listing = Listing.objects.create(
            title=listing_data["title"],
            description=listing_data["description"],
            starting_bid=listing_data["starting_bid"],
            current_bid=listing_data["starting_bid"],
            category=listing_data["category"],
            image=listing_data["image"],
            user=users[i % len(users)],
            active=True,
        )
        # Actualizar fecha de creación
        listing.created = created_date
        listing.save()
        listings.append(listing)
        print(f"   ✅ Subasta creada: {listing.title}")

    # Crear pujas
    print("💰 Creando pujas...")
    bid_count = 0
    for listing in listings[:7]:  # Solo para las primeras 7 subastas
        num_bids = (hash(listing.title) % 5) + 1  # 1-5 pujas por subasta
        current_bid = listing.starting_bid

        for j in range(num_bids):
            # Incrementar puja entre 10-50
            increment = Decimal(str((hash(f"{listing.id}{j}") % 40) + 10))
            current_bid += increment

            # Seleccionar usuario diferente al creador
            available_users = [u for u in users if u != listing.user]
            if available_users:
                bidder = available_users[
                    (hash(f"{listing.id}{j}") % len(available_users))
                ]
            else:
                continue  # Skip if no available users

            # Crear fecha de puja
            days_since_listing = (hash(f"{listing.id}{j}") % 7) + 1
            bid_date = listing.created + timedelta(days=days_since_listing)

            bid = Bid.objects.create(listing=listing, user=bidder, amount=current_bid)
            bid.created_at = bid_date
            bid.save()

            # Actualizar puja actual de la subasta
            listing.current_bid = current_bid
            listing.save()

            bid_count += 1
            print(
                f"   ✅ Puja creada: ${current_bid} por {bidder.username} en {listing.title}"
            )

    # Crear comentarios
    print("💬 Creando comentarios...")
    comments_data = [
        "¿Está en buenas condiciones?",
        "¿Incluye garantía?",
        "Excelente producto, muy interesado",
        "¿Aceptas ofertas directas?",
        "¿Cuándo termina la subasta?",
        "¿Tienes más fotos?",
        "¿El envío está incluido?",
        "Muy buen precio",
        "¿Es original?",
        "¿Dónde te encuentras?",
    ]

    comment_count = 0
    for listing in listings[:6]:  # Comentarios para las primeras 6 subastas
        num_comments = (hash(listing.title) % 3) + 1  # 1-3 comentarios por subasta

        for j in range(num_comments):
            commenter = users[(hash(f"{listing.id}{j}") % len(users))]
            comment_text = comments_data[comment_count % len(comments_data)]

            # Crear fecha de comentario
            days_since_listing = (hash(f"{listing.id}{j}") % 10) + 1
            comment_date = listing.created + timedelta(days=days_since_listing)

            comment = Comment.objects.create(
                listing=listing, user=commenter, text=comment_text
            )
            comment.created = comment_date
            comment.save()

            comment_count += 1
            print(
                f"   ✅ Comentario creado por {commenter.username} en {listing.title}"
            )

    # Crear listas de seguimiento
    print("⭐ Creando listas de seguimiento...")
    watchlist_count = 0
    for user in users[:4]:  # Solo para los primeros 4 usuarios
        num_watchlist = (hash(user.username) % 3) + 1  # 1-3 items en watchlist

        for j in range(num_watchlist):
            listing = listings[(hash(f"{user.id}{j}") % len(listings))]

            # Evitar que el usuario agregue su propia subasta
            if listing.user != user:
                watchlist, created = Watchlist.objects.get_or_create(
                    user=user, listing=listing, defaults={"active": True}
                )
                if created:
                    watchlist_count += 1
                    print(
                        f"   ✅ {user.username} agregó {listing.title} a su lista de seguimiento"
                    )

    # Estadísticas finales
    print("\n📊 Resumen de datos creados:")
    print(f"   👥 Usuarios: {User.objects.count()}")
    print(f"   🏷️ Subastas: {Listing.objects.count()}")
    print(f"   💰 Pujas: {Bid.objects.count()}")
    print(f"   💬 Comentarios: {Comment.objects.count()}")
    print(f"   ⭐ Items en watchlist: {Watchlist.objects.count()}")
    print(
        f"   📈 Categorías únicas: {Listing.objects.values('category').distinct().count()}"
    )

    print("\n🎉 ¡Datos de prueba cargados exitosamente!")
    print("\n📝 Credenciales de usuarios:")
    print("   Admin: admin / admin123")
    print("   Usuarios: [username] / password123")
    print("   Ejemplo: juan_perez / password123")


if __name__ == "__main__":
    create_test_data()
