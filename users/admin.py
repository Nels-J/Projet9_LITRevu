from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):  # permet d'adapter l'interface admin (backoffice) pour la gestion utilisateur (gestion des roles par exemple si on en avait besoin)
    pass