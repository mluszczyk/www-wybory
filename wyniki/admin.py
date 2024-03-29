from django.contrib import admin
from wyniki import models

admin.site.register(models.Wojewodztwo)
admin.site.register(models.Gmina)
admin.site.register(models.Wynik)


class KandydatAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions


admin.site.register(models.Kandydat, KandydatAdmin)
