from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User, UserFollows, Review, Ticket


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class FollowUserForm(forms.ModelForm):
    """
    Formulaire de création d'un abonnement (UserFollows).

    Le modèle stocke (persiste) deux FK :
    - user : l'utilisateur connecté qui suit
    - followed_user : l'utilisateur suivi

    L'interface n'expose qu'un champ texte `username`.
    Ce champ est validé puis converti en instance `User` dans `clean_username`.
    """
    username = forms.CharField(
            max_length=150,
            label="Saisir le nom de l'utilisateur que vous souhaitez suivre :",
            widget=forms.TextInput(
                    attrs={
                            "placeholder": "Nom d'utilisateur à suivre",
                            "autocomplete": "off",
                    },
            ),
    )

    class Meta:
        model = UserFollows
        fields = [
                "user",   # utilisateur connecté (rempli côté serveur)
                "followed_user"  # utilisateur suivi (résolu depuis username)
        ]

    def __init__(self, *args, user=None, **kwargs):
        """
        Reçoit l'utilisateur connecté via `user=...` (injecté par la vue).

        Les champs FK du ModelForm sont masqués et non requis :
        ils sont définis de manière sûre dans `save()`.
        """
        super().__init__(*args, **kwargs)
        self.user = user
        # On masque les champs FK générés par ModelForm, ils seront remplis dans save()
        self.fields["user"].required = False
        self.fields["user"].widget = forms.HiddenInput()
        self.fields["followed_user"].required = False
        self.fields["followed_user"].widget = forms.HiddenInput()

    def clean_username(self) -> User:
        """
        Valide le pseudo saisi via le champ username et retourne l'objet User
        - Valide si utilisateur cible existe, ne se suit pas lui même, relation n'existe pas déjà.
        Retourne l'instance User cible (stockée dans cleaned_data["username"]).
        """
        username = self.cleaned_data["username"].strip()   # champs custom, gérés manuellement

        try:
            followed_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Cet utilisateur n'existe pas.")

        if followed_user == self.user:
            raise forms.ValidationError("Vous ne pouvez pas vous suivre vous-même.")

        if UserFollows.objects.filter(user=self.user, followed_user=followed_user).exists():
            raise forms.ValidationError("Vous suivez déjà cet utilisateur.")

        return followed_user  # stocké dans cleaned_data["username"] (nom du champ custom)

    def save(self, commit=True) -> User:
        """
        Crée la relation UserFollows en affectant explicitement les FK :
        - user = utilisateur connecté ;
        - followed_user = utilisateur retourné par `clean_username`.

        Ne fait pas confiance aux données POST pour ces champs FK.
        """
        instance = super().save(commit=False)
        instance.user = self.user
        instance.followed_user = self.cleaned_data["username"]  # retourné par clean_username
        if commit:
            instance.save()
        return instance


class CreateReviewAndTicketForm(forms.Form):
    # Champs pour le Ticket
    title = forms.CharField(max_length=128, label="Titre")
    description = forms.CharField(widget=forms.Textarea, label="Description", required=False)
    image = forms.ImageField(label="Image", required=False)

    # Champs pour la Review
    headline = forms.CharField(max_length=128, label="Titre")
    rating = forms.TypedChoiceField(
            choices=Review.Rating.choices,
            coerce=int,
            label="Note",
            widget=forms.RadioSelect,
    )

    body = forms.CharField(widget=forms.Textarea, label="Commentaire", required=False)

    def save(self, user):
        # Création du Ticket
        ticket = Ticket.objects.create(
            title=self.cleaned_data['title'],
            description=self.cleaned_data['description'],
            image=self.cleaned_data['image'],
            user=user
        )

        # Création de la Review associée au Ticket
        review = Review.objects.create(
            ticket=ticket,
            headline=self.cleaned_data['headline'],
            rating=self.cleaned_data['rating'],
            body=self.cleaned_data['body'],
            user=user
        )

        return review  # Retourne la review créée (le ticket est accessible via review.ticket)


class ReviewForm(forms.ModelForm):

    class Meta:
        model = Review
        fields = ['headline', 'body', 'rating']
        widgets = {
                'rating': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['rating'].choices = Review.Rating.choices

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
