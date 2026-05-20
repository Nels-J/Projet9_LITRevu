from itertools import chain

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, TemplateView

from users.forms import UserCreateForm, FollowUserForm, ReviewForm, TicketForm
from users.models import Ticket, Review, UserFollows

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


class FluxView(LoginRequiredMixin, ListView):
    template_name = 'users/flux.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        # Liste les IDs des utilisateurs suivis par l'utilisateur connecté
        followed_user_ids = UserFollows.objects.filter(
            user=self.request.user
        ).values_list('followed_user_id', flat=True)

        # Ajoute à la liste des utilisateurs ciblés, l'utilisateur connecté
        visible_user_ids = list(followed_user_ids) + [self.request.user.id]

        # Sélectionne Tickets et Reviews correspondant aux utilisateurs ciblés.
        tickets = Ticket.objects.filter(
            user_id__in=visible_user_ids
        ).select_related('user')

        # todo: a vérifier une fois les Review possible - non implémenté
        reviews = Review.objects.filter(
            user_id__in=visible_user_ids
        ).select_related('user', 'ticket', 'ticket__user')

        # Fusion + tri du plus récent au plus ancien
        return sorted(
            chain(tickets, reviews),
            key=lambda post: post.time_created,
            reverse=True,
        )


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
                reverse=True,  # inverse le tri (+ récent en premier)
        )


class AbonnementsView(LoginRequiredMixin, CreateView):
    """
    Page des abonnements :
    - GET  : affiche le formulaire + listes following/followers
    - POST : tente de créer une relation UserFollows
    """
    template_name = 'users/abonnements.html'
    form_class = FollowUserForm
    success_url = reverse_lazy('abonnements')

    def get_form_kwargs(self):
        """
        Injecte l'utilisateur connecté dans le formulaire.

        Le formulaire l'utilise pour interdire auto-follow, pas doublons, renseigner 'user' lors du save.
        """
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user  # utilisateur connecté (A)
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Ajoute au contexte du template :
        - `following` : utilisateurs suivis par l'utilisateur connecté 'request.user'
        - `followers` : utilisateurs qui suivent l'utilisateur connecté 'request.user'
        """
        context = super().get_context_data(**kwargs)
        context['following'] = UserFollows.objects.filter(user=self.request.user).select_related('followed_user')
        context['followers'] = UserFollows.objects.filter(followed_user=self.request.user).select_related('user')
        return context


class UnfollowView(LoginRequiredMixin, DeleteView):
    model = UserFollows
    pk_url_kwarg = 'follow_id'
    success_url = reverse_lazy('abonnements')

    def get_queryset(self) -> QuerySet:
        """Restreint la suppression aux abonnements de l'utilisateur connecté.
           En filtrant le queryset avec self.request.user
        """
        return UserFollows.objects.filter(user=self.request.user)


class CreateReviewView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'users/review_create.html'
    success_url = reverse_lazy('flux')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CreateTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'users/ticket_create.html'
    success_url = reverse_lazy('flux')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CreateResponseView(LoginRequiredMixin, TemplateView):
    """ Création d'une Review en réponse à un Ticket existant. L'ID du Ticket parent est passé en paramètre d'URL."""
    template_name = 'users/response_create.html'

    def dispatch(self, request, *args, **kwargs):
        self.ticket = get_object_or_404(
            Ticket,
            pk=kwargs['pk']
        )

        return super().dispatch(
            request,
            *args,
            **kwargs
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ticket'] = self.ticket
        context['review_form'] = ReviewForm()

        return context

    def post(self, request, *args, **kwargs):
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.ticket = self.ticket
            review.user = self.request.user
            review.save()

            return redirect('flux')

        return self.render_to_response({
                'review_form': review_form,
                'ticket': self.ticket,
        })


class UpdateTicketView(LoginRequiredMixin, UserPassesTestMixin , UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = 'users/ticket_update.html'
    success_url = reverse_lazy('posts')

    def test_func(self) -> bool :
        """Vérifie si le ticket appartient bien l'utilisateur connecté, sinon une 403 sera rendu via la class
        UserPassesTestMixin"""
        ticket = self.get_object()
        return ticket.user == self.request.user


class DeleteTicketView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ticket
    template_name = 'users/ticket_confirm_delete.html'
    success_url = reverse_lazy('posts')

    def test_func(self) -> bool :
        """Vérifie si le ticket appartient bien l'utilisateur connecté, sinon une 403 sera rendu via la class
        UserPassesTestMixin"""
        ticket = self.get_object()
        return ticket.user == self.request.user
