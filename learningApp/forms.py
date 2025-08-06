from django import forms
# from .models import UserProfile # No longer needed

class UserProfileForm(forms.Form):
    LEARNING_STYLE_CHOICES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditory'),
        ('kinesthetic', 'Kinesthetic'),
    ]

    SKILL_LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    learning_style = forms.ChoiceField(choices=LEARNING_STYLE_CHOICES, required=False)
    preferred_subjects = forms.CharField(max_length=255, required=False, help_text="Comma-separated or similar")
    skill_level = forms.ChoiceField(choices=SKILL_LEVEL_CHOICES, required=False)
    specific_goals = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput) 