from itertools import chain
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView as DjangoLoginView,
    LogoutView as DjangoLogoutView,
)
from django.db.models import QuerySet, Q
from django.http import HttpResponse, HttpResponseBase
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DeleteView, UpdateView, FormView

from users.forms import (
    UserCreateForm,
    FollowUserForm,
    ReviewForm,
    TicketForm,
    CreateReviewAndTicketForm,
)
from users.models import Ticket, Review, UserFollows

User = get_user_model()


class LoginView(DjangoLoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True


class LogoutView(DjangoLogoutView):
    pass


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = UserCreateForm
    success_url = reverse_lazy(settings.LOGIN_REDIRECT_URL)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class FluxView(LoginRequiredMixin, ListView):
    template_name = "users/flux.html"
    context_object_name = (
        "items"  # Renomme le contexte pour le template (au lieu de 'object_list')
    )

    def get_queryset(self):
        # Liste les IDs des utilisateurs suivis par l'utilisateur connecté
        followed_user_ids = UserFollows.objects.filter(
            user=self.request.user
        ).values_list("followed_user_id", flat=True)

        # Ajoute à la liste des utilisateurs ciblés, l'utilisateur connecté
        visible_user_ids = list(followed_user_ids) + [self.request.user.id]

        # Sélectionne Tickets et Reviews des utilisateurs ciblés.
        tickets = (
            Ticket.objects.filter(user_id__in=visible_user_ids)
            .select_related("user")
            .prefetch_related("reviews")
        )

        reviews = Review.objects.filter(
                # Review écrite par un utilisateur visible
                Q(user_id__in=visible_user_ids)
                |
                # Review liée à un ticket appartenant à un utilisateur visible
                Q(ticket__user_id__in=visible_user_ids)
        ).select_related(
                "user",             # auteur de la review
                "ticket",           # ticket associé
                "ticket__user"      # auteur du ticket associé (pour affichage dans flux)
        )

        # Fusion + tri du plus récent au plus ancien
        return sorted(
            chain(tickets, reviews),
            key=lambda post: post.time_created,
            reverse=True,
        )


class PostsView(LoginRequiredMixin, ListView):
    template_name = "users/posts.html"
    context_object_name = (
        "items"  # Renomme le contexte pour le template (au lieu de 'object_list')
    )

    def get_queryset(self):
        # QuerySet des tickets et reviews de l'utilisateur connecté
        tickets = Ticket.objects.filter(user=self.request.user).prefetch_related("reviews")
        tickets_reviews = Review.objects.filter(
                Q(user=self.request.user)           # reviews écrites par l'utilisateur connecté.
                |
                Q(ticket__user=self.request.user)   # reviews écrites par XYZ sur les tickets de l'utilisateur connecté.
        ).select_related("user", "ticket", "ticket__user")

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

    template_name = "users/abonnements.html"
    form_class = FollowUserForm
    success_url = reverse_lazy("abonnements")

    def get_form_kwargs(self):
        """
        Injecte l'utilisateur connecté dans le formulaire.

        Le formulaire l'utilise pour interdire auto-follow, pas doublons, renseigner 'user' lors du save.
        """
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user  # utilisateur connecté (A)
        return kwargs

    def get_context_data(self, **kwargs):
        """
        Ajoute au contexte du template :
        - `following` : utilisateurs suivis par l'utilisateur connecté 'request.user'
        - `followers` : utilisateurs qui suivent l'utilisateur connecté 'request.user'
        """
        context = super().get_context_data(**kwargs)
        context["following"] = UserFollows.objects.filter(
            user=self.request.user
        ).select_related("followed_user")
        context["followers"] = UserFollows.objects.filter(
            followed_user=self.request.user
        ).select_related("user")
        return context


class UnfollowView(LoginRequiredMixin, DeleteView):
    model = UserFollows
    pk_url_kwarg = "follow_id"
    success_url = reverse_lazy("abonnements")

    def get_queryset(self) -> QuerySet[UserFollows]:
        """Restreint la suppression aux abonnements de l'utilisateur connecté.
        En filtrant le queryset avec self.request.user
        """
        assert self.request.user.is_authenticated
        return UserFollows.objects.filter(user=self.request.user)


class CreateReviewView(LoginRequiredMixin, FormView):
    model = Review
    form_class = CreateReviewAndTicketForm
    template_name = "users/review_create.html"
    success_url = reverse_lazy("flux")

    def form_valid(self, form):
        """Assigne l'utilisateur connecté à la review avant de la sauvegarder.
        En assignant form.instance.user dans form_valid() on s'assure que l'utilisateur est défini de manière sûre,
        indépendamment des données POST (champ user masqué dans le formulaire).
        """
        form.save(user=self.request.user)
        return super().form_valid(form)  # renvoi


class CreateTicketView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketForm
    template_name = "users/ticket_create.html"
    success_url = reverse_lazy("flux")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CreateResponseView(LoginRequiredMixin, CreateView):
    """
    Crée une Review en réponse à un Ticket existant.

    - Charge le ticket parent depuis l'URL (pk).
    - Expose ce ticket au template.
    - Crée la review en assignant user connecté et ticket au formulaire avant sauvegarde. (commit)
    """

    model = Review
    form_class = ReviewForm
    template_name = "users/response_create.html"
    success_url = reverse_lazy("flux")
    ticket: Ticket | None = None  # Attribut d'instance pour stocker le ticket parent chargé dans dispatch()

    def dispatch(self, request, *args, **kwargs) -> HttpResponseBase:
        """Prépare la vue avant routage GET/POST."""
        self.ticket = get_object_or_404(
            Ticket.objects.select_related("user"),
                pk=kwargs["pk"]
        )

        # Une seule review autorisée par ticket.
        if Review.objects.filter(ticket=self.ticket).exists():
            messages.warning(
                request,
                "Ce ticket a déjà une critique, vous ne pouvez pas en ajouter une nouvelle.",
            )
            return redirect("flux")

        return super().dispatch(
            request, *args, **kwargs
        )  # L'instance CreateView gère le routage GET/POST.

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Enrichit le contexte du template."""
        context = super().get_context_data(
            **kwargs
        )  # Contexte fourni par CreateView (le formulaire)
        context["ticket"] = (
            self.ticket
        )  # Ajout du ticket parent au contexte pour affichage dans le template.
        return context

    def form_valid(self, form) -> HttpResponse:
        form.instance.user = self.request.user
        form.instance.ticket = self.ticket
        return super().form_valid(form)


class UpdateTicketView(LoginRequiredMixin, UpdateView):
    model = Ticket
    form_class = TicketForm
    template_name = "users/ticket_update.html"
    success_url = reverse_lazy("posts")

    def get_queryset(self):
        return (
            super().get_queryset().select_related("user").filter(user=self.request.user)
        )


class DeleteTicketView(LoginRequiredMixin, DeleteView):
    model = Ticket
    template_name = "users/ticket_confirm_delete.html"
    success_url = reverse_lazy("posts")

    def get_queryset(self):
        return (
            super().get_queryset().select_related("user").filter(user=self.request.user)
        )


class UpdateReviewView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = "users/review_update.html"
    success_url = reverse_lazy("posts")

    def get_queryset(self):
        return (
            super().get_queryset().select_related("user").filter(user=self.request.user)
        )


class DeleteReviewView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = "users/review_confirm_delete.html"
    success_url = reverse_lazy("posts")

    def get_queryset(self):
        return (
            super().get_queryset().select_related("user").filter(user=self.request.user)
        )
