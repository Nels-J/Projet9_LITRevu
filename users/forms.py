from django import forms
from django.contrib.auth.forms import UserCreationForm

from users.models import User, UserFollows


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User


class FollowUserForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label="Nom d'utilisateur à suivre")

    class Meta:
        model = UserFollows
        fields = []  # on n'expose pas directement user/followed_user

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self._followed_user = None

    def clean_username(self):
        username = self.cleaned_data["username"].strip()

        try:
            followed_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError("Cet utilisateur n'existe pas.")

        if followed_user == self.user:
            raise forms.ValidationError("Vous ne pouvez pas vous suivre vous-même.")

        if UserFollows.objects.filter(user=self.user, followed_user=followed_user).exists():
            raise forms.ValidationError("Vous suivez déjà cet utilisateur.")

        self._followed_user = followed_user

        return username

    def save(self, commit=True):
        if self._followed_user is None:
            raise ValueError("FollowUserForm.save() appelé sans validation préalable (is_valid()).")

        instance = super().save(commit=False)  # ne sauvegarde pas immédiatement permet d'assigner les champs user et followed_user
        instance.user = self.user
        instance.followed_user = self._followed_user
        if commit:  # Si commit est True, alors on sauvegarde l'instance dans la base de données
            instance.save()

        return instance
