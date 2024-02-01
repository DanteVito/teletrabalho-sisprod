
from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    search_fields = ('nome', 'username', 'rg', )
    list_display = ('username', 'nome', 'cargo')
    fields = ('nome', 'username', 'rg', 'cargo',
              'ramal', 'celular', 'email', 'cidade', 'groups', 'is_active')

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = User.objects.filter(id=request.user.id)  # noqa E501
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'servidor':
                kwargs["queryset"] = User.objects.filter(id=request.user.id)  # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj):
        if request.user.is_superuser:
            return ()
        return ('groups', 'is_active')


admin.site.register(User, UserAdmin)
