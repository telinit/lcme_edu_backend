from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.forms import forms, ModelForm
from reversion.admin import VersionAdmin

from .models import *


# @admin.register(User)
# class UserAdmin(VersionAdmin, UserAdmin, ModelAdmin):
#     pass


class UserCreationForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(VersionAdmin, UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ('username', 'last_name', 'first_name', 'middle_name')
    ordering = ('username', 'last_name', 'first_name', 'middle_name')

    f = ('username', 'email', 'password', 'pw_enc',
         'first_name', 'middle_name', 'last_name',
         'is_superuser', 'is_staff', 'is_active',
         'avatar', 'children')

    fieldsets = (
        (None, {'fields': f}),
        )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': f}
            ),
        )

    filter_horizontal = ()


admin.site.register(User, CustomUserAdmin)
