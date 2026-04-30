from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Ticket, Review


# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    '''
        Permet d'adapter l'interface admin (backoffice) pour
        la gestion utilisateur (gestion des roles par exemple si on en avait besoin)
     '''


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    '''
        Permet d'adapter l'interface admin (backoffice) pour la gestion des tickets
    '''


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    '''
        Permet d'adapter l'interface admin (backoffice) pour la gestion des reviews
    '''

