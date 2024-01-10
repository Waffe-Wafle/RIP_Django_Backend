from django.contrib.admin import site, TabularInline, ModelAdmin
from SoftLoading.models import Soft, File, Payment


class FilesTabular(TabularInline):
    model = File
    extra = 0


class SoftView(ModelAdmin):
    inlines = [FilesTabular]


class SoftTabular(TabularInline):
    model = Payment.soft.through
    can_delete = False

    def has_add_permission(self, *args):
        return False

    def has_change_permission(self, *args):
        return False


class PaymentsView(ModelAdmin):
    inlines = [SoftTabular]
    exclude = ['soft']
    readonly_fields = ['date_open', 'date_close', 'user', 'code', 'manager', 'date_pay']
    can_delete = False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.manager = request.user
        obj.save()


site.register(Soft, SoftView)
site.register(Payment, PaymentsView)
