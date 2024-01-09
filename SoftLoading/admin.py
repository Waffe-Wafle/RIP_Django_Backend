from django.contrib.admin import site, TabularInline, ModelAdmin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from SoftLoading.models import Soft, File, Payment

# site.register([Soft, File, Payment])


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


site.register(Soft, SoftView)
site.register(Payment, PaymentsView)
