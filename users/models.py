from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator
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
        ordering = ['-time_created']

    def __str__(self):
        return f"{self.title} - {self.description} - by: {self.user}"

    @property
    def has_review(self):
        # return self.reviews.exists()  # Vérifie si une review est associée à ce ticket
       return Review.objects.filter(ticket=self).exists()  # Alternative plus explicite


class Review(models.Model):
    ticket = models.ForeignKey(to=Ticket, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(
            validators=[MaxValueValidator(5)]
)
    headline = models.CharField(max_length=128)
    body = models.CharField(max_length=8192, blank=True)
    user = models.ForeignKey(
            to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
    )
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_created']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'ticket'],
                name='unique_user_review_per_ticket',
            ),
            # Condition pour renforcer l'intégrité niveau DB en sus de PositiveSmallIntegerField niveau champ.
            models.CheckConstraint(
                condition=models.Q(rating__gte=0, rating__lte=5),
                name='rating_between_0_and_5',
            ),
        ]

    def __str__(self):
        return f"{self.headline} - {self.rating} - by: {self.user}"


class UserFollows(models.Model):
    user = models.ForeignKey(
            to=settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='following',
    )
    followed_user = models.ForeignKey(
            to=settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='followed_by',
    )

    class Meta:
        constraints = [
                models.UniqueConstraint(
                        fields=['user', 'followed_user'],
                        name='unique_user_follow_pair',
                ),
                models.CheckConstraint(
                        condition=~models.Q(user=models.F('followed_user')),
                        name='prevent_self_follow',
                ),
        ]

    def __str__(self):
        return f"{self.user.username} -> {self.followed_user.username}"
