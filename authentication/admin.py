""" authentication admin.py """

from django.contrib import admin
from allauth.account.decorators import secure_admin_login

from .models import User


class UserAdmin(admin.ModelAdmin):
    """
    Modelo para usuários
    """

    search_fields = (
        "nome",
        "username",
        "rg",
    )
    list_display = (
        "username",
        "nome",
    )
    fields = (
        "nome",
        "username",
        "rg",
        "groups",
        "is_active",
        "is_superuser",
    )

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = User.objects.filter(id=request.user.id)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "servidor":
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return ()
        return ("groups", "is_active", "is_superuser")


admin.autodiscover()
admin.site.login = secure_admin_login(admin.site.login)