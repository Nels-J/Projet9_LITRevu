from users.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    """Formulaire de modification d'utilisateur personnalisé."""
    class Meta(UserCreationForm.Meta):
        model = User