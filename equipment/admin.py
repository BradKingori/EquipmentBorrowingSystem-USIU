from django.contrib import admin
#from .models import Student,BorrowRequest,Equipment

#admin.site.register(Equipment)
#admin.site.register(BorrowRequest)
#admin.site.register(Student)
# Register your models here.

from django.contrib import admin
from django.apps import apps


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass

"""
#Restricting user permissions in Admin interface
from .models import Equipment

class EquipmentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return True
    def has_delete_permission(self, request, obj=None):
        return True
    def has_change_permission(self, request, obj=None):
        return True

"""
