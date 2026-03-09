from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from django.contrib.auth.views import(
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.views.generic import TemplateView, FormView

User = get_user_model()

# Create your views here.
class IndexView(LoginRequiredMixin, TemplateView):
    """Page d'accueil protégée par authentification."""
    template_name = 'users/index.html'
    login_url = "users:login"

    def get_context_data(self, **kwargs):
        """Ajoute le nom d'utilisateur au contexte."""
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context


class LoginView(DjangoLoginView):
    """Connexion utilisateur."""
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    """Déconnexion utilisateur."""
    pass # LOGOUT_REDIRECT_URL est défini dans settings.py


class RegisterView(FormView):
    """Inscription d'un nouvel utilisateur."""
    template_name = 'users/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        """Crée l'utilisateur et redirige vers login."""
        form.save()
        return super().form_valid(form)


class FluxView(TemplateView):
    template_name = 'users/flux.html'  # ou votre template


class PostsView(TemplateView):
    template_name = 'users/posts.html'


class AbonnementsView(TemplateView):
    template_name = 'users/abonnements.html'
