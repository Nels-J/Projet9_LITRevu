from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from django.contrib.auth.views import(
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.views.generic import TemplateView, FormView, CreateView
from django.conf import settings

from users.forms import UserCreateForm

User = get_user_model()

class IndexView(LoginRequiredMixin, TemplateView):  # Protégée
    template_name = 'users/index.html'
    login_url = settings.LOGIN_URL  # Redirection si user non connecté via CONSTANTE dans settings.py

    def get_context_data(self, **kwargs):
        """Ajoute le nom d'utilisateur au contexte."""
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        return context


class LoginView(DjangoLoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    pass # LOGOUT_REDIRECT_URL est défini dans settings.py donc rien à faire todo a vérifier avec Pablo.


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = UserCreateForm
    success_url = reverse_lazy(settings.LOGIN_URL)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FluxView(LoginRequiredMixin,TemplateView):
    template_name = 'users/flux.html'
    login_url = settings.LOGIN_URL


class PostsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/posts.html'
    login_url = settings.LOGIN_URL


class AbonnementsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/abonnements.html'
    login_url = settings.LOGIN_URL
