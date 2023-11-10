from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from users.models import User, Subscribe


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name', 'last_name', 'is_superuser',
        'is_active', 'date_joined'
    )
    list_filter = ('email', 'username')
    list_display_links = ('username',)
    search_fields = ('username',)
    fieldsets = (
        (None, {'fields': ('username', 'first_name', 'last_name', 'email')}),
        ('Права', {'fields': ('is_staff', 'is_active')})
    )
    add_fieldsets = (
        (None, {'fields': (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', 'is_staff', 'is_active'
        )}),
    )


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


@admin.register(Subscribe)
class FollowAdmin(admin.ModelAdmin):
    form = SubscribeAdminForm
    list_display = ('id', 'user', 'author')
    list_display_links = ('user',)
    search_fields = ('user',)

    def save_model(self, request, obj, form, change):
        if obj.user == obj.author:
            # Add a non-field error to the form
            form.add_error(None, ValidationError(
                'You cannot subscribe to yourself.'))
        else:
            super().save_model(request, obj, form, change)
