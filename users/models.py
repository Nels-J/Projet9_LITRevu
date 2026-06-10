from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    def __str__(self):
        return self.username


class Ticket(models.Model):
    title = models.CharField(max_length=128)
    description = models.TextField(max_length=2048, blank=True)
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="tickets/", null=True, blank=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-time_created"]

    def __str__(self):
        return f"{self.title} - {self.description} - by: {self.user}"

    @property
    def has_review(self):
        """
        Vérif. de l'existence de review lié au ticket.
         - Si des reviews ont été préchargées (via prefetch_related), utilise le cache (réduire sql n+1).
         - Sinon, éxécute la requête traditionnelle pour vérifier l'existence de review liée au ticket.
         - Renvoi True si au moins une review existe, sinon False.
        """
        prefetched_reviews = getattr(self, "_prefetched_objects_cache", {}).get(
            "reviews"
        )
        if prefetched_reviews is not None:
            return bool(prefetched_reviews)
        return self.reviews.exists()


class Review(models.Model):
    ticket = models.ForeignKey(
        to=Ticket, on_delete=models.CASCADE, related_name="reviews"
    )

    class Rating(models.IntegerChoices):
        ZERO = 0, "0"
        ONE = 1, "1"
        TWO = 2, "2"
        THREE = 3, "3"
        FOUR = 4, "4"
        FIVE = 5, "5"

    rating = models.PositiveSmallIntegerField(
        choices=Rating.choices,
    )

    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)

    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-time_created"]
        constraints = [
            # Garantir l'unicité : un ticket ne peut avoir qu'une seule et unique review.
            models.UniqueConstraint(
                fields=["ticket"],
                name="unique_review_per_ticket",
            ),
            # Renforcer l'intégrité niveau DB en sus de PositiveSmallIntegerField niveau champ.
            models.CheckConstraint(
                condition=models.Q(
                        rating__gte=0,
                        rating__lte=5
                ),
                name="rating_between_0_and_5",
            ),
        ]

    def __str__(self):
        return f"{self.headline} - {self.rating} - by: {self.user}"


class UserFollows(models.Model):
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following",
    )
    followed_user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="followed_by",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "followed_user"],
                name="unique_user_follow_pair",
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F("followed_user")),
                name="prevent_self_follow",
            ),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.followed_user.username}"
