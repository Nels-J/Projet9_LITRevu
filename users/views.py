from itertools import chain

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView

from users.forms import UserCreateForm
from users.models import Ticket, Review

User = get_user_model()


class LoginView(DjangoLoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    pass


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreateForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FluxView(LoginRequiredMixin, TemplateView):
    ''' Affiche les posts des utilisateurs à l'utilisateur connecté.
        LoginRequiredMixin : Assure que l'utilisateur est connecté pour accéder à la vue définie par template_name.
        Sinon, redirection vers la page de connexion à l'aide de la constante LOGIN_URL défini dans settings.py
        TemplateView : Affiche un template HTML.
        template_name : Spécifie le template à utiliser pour afficher la vue.
    '''
    template_name = 'users/flux.html'


class PostsView(LoginRequiredMixin, ListView):
    template_name = 'users/posts.html'
    context_object_name = 'posts'  # Renomme le contexte pour accéder aux posts dans le template

    def get_queryset(self):

        # QuerySet des tickets et reviews de l'utilisateur connecté
        tickets = Ticket.objects.filter(user=self.request.user)
        tickets_reviews = Review.objects.filter(user=self.request.user).select_related('ticket')

        # Combinaison tickets & reviews triés.
        return sorted(
                # chain combiner les deux QuerySet en une seule séquence itérable
                chain(tickets, tickets_reviews),
                key=lambda post: post.time_created,  # clé de tri.
                reverse=True  # inverse le tri (+ récent en premier)
        )

        context['posts'] = posts
        return context

class AbonnementsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/abonnements.html'
