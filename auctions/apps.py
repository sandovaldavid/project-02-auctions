from django.apps import AppConfig


class AuctionsConfig(AppConfig):
    name = "auctions"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import auctions.notifications.signals  # noqa: F401
