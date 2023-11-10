from django import forms
from django.core.exceptions import ValidationError

from users.models import Subscribe


class SubscribeAdminForm(forms.ModelForm):
    class Meta:
        model = Subscribe
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        author = cleaned_data.get('author')
        if user and author and user == author:
            raise ValidationError('Нельзя подписаться на самого себя')
        return cleaned_data
