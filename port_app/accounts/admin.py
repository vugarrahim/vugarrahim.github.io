from django.contrib import admin
from .models import *
from .forms import *
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'telephone', 'passport')}),
        (_('Permissions'), {'fields': ('is_active', 'is_admin', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ("first_name", "last_name", "telephone", 'passport', 'email', 'password1', 'password2'),
        }),
    )
    # The forms to add and change user instances
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'first_name', 'last_name', 'telephone', 'passport', 'is_admin')
    list_filter = ('is_admin', 'is_superuser', 'is_active', 'groups')
    search_fields = ('first_name', 'last_name', 'email', 'telephone', 'passport')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)

    # def has_delete_permission(self, request, obj=None):
    #     if request.user.groups.filter(name="Developer").exists():
    #         return True
    #     return False

    # def get_actions(self, request):
    #     """
    #         Disables native delete() function of admin which physically deletes
    #         information from database
    #     """
    #     actions = super(MyUserAdmin, self).get_actions(request)
    #     if not request.user.groups.filter(name="Developer").exists():
    #         del actions['delete_selected']
    #
    #     return actions

admin.site.register(MyUser, MyUserAdmin)

admin.site.register(Agent)
