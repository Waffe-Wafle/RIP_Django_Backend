from django.contrib.admin import site, TabularInline, ModelAdmin
from SoftLoading.models import Soft, File, Payment


class FilesTabular(TabularInline):
    model = File
    extra = 0


class SoftView(ModelAdmin):
    inlines = [FilesTabular]


class SoftTabular(TabularInline):
    model = Payment.soft.through
    extra = 0


class PaymentsView(ModelAdmin):
    inlines = [SoftTabular]
    exclude = ['soft']
    readonly_fields = ['date_open', 'date_close', 'code', 'manager']


site.register(Soft, SoftView)
site.register(Payment, PaymentsView)
