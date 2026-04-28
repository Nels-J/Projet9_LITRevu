from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.views.generic import TemplateView, CreateView

from users.forms import UserCreateForm

User = get_user_model()


class LoginView(DjangoLoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    pass


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreateForm
    success_url = settings.LOGIN_REDIRECT_URL

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


class PostsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/posts.html'


class AbonnementsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/abonnements.html'
