from django.db import models
from django.core.validators import MinValueValidator

from .validators import *
from django.contrib.auth.models import User

from django.dispatch import receiver
from django.db.models.signals import post_save
from os.path import getsize
from django.utils.timezone import now

from hashlib import sha256
from Site.settings import SOFT_LOADERS_ROOT, PHOTOS_ROOT


class Soft(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True, upload_to=PHOTOS_ROOT)
    description = models.TextField(blank=True, null=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(max_length=9,
                              default=SOFT_STATUSES[0],
                              validators=[soft_status_validate],
                              choices=[(var, var) for var in SOFT_STATUSES])

    class Meta:
        managed = True
        db_table = 'Soft'

    def __str__(self):
        return f'{self.name} ({self.price} ₽)'


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T']:
        if abs(num) < 1000:
            return '%3.1f %s%s' % (num, unit, suffix)
        num /= 1024.0
    raise ValueError('Too big file size!')


class File(models.Model):
    soft = models.ForeignKey(Soft, models.CASCADE)
    file = models.FileField(upload_to=SOFT_LOADERS_ROOT)
    size = models.CharField(max_length=9, blank=True, null=False, editable=False)
    platform = models.CharField(
        max_length=100, blank=True, null=True,
        validators=[file_platform_validate],
        choices=[(var, var) for var in PLATFORMS]
    )
    architecture = models.CharField(
        max_length=3, blank=True, null=True,
        validators=[file_architecture_validate],
        choices=[(var, var) for var in ARCHITECTURES]
    )
    comment = models.TextField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'Files'

    def __str__(self):
        return f'{self.soft.name} ({self.file.name.split(".")[-1]}): ' \
               f' {self.platform}-{self.architecture}'


@receiver(post_save, sender=File)
def save_size(sender, instance, *args, **kwargs):          # Used signal instead of save
    size = sizeof_fmt(instance.file.size)                  # because of path of unsaved file bug.
    instance.size = size                                   # To be correctly returned in current request
    File.objects.filter(id=instance.id).update(size=size)  # To save properly in model without recursion




class Payment(models.Model):
    soft = models.ManyToManyField(Soft)
    user = models.ForeignKey(User, models.CASCADE)
    manager = models.ForeignKey(User, models.SET_NULL,
                                related_name='payment_from_manager_set', blank=True, null=True,
                                editable=False)
    code = models.CharField(max_length=10, blank=True, null=False, editable=False)
    status = models.CharField(
        max_length=9,
        blank=True,
        default=PAYMENT_STATUSES[0],
        validators=[payment_status_validate],
        choices=[(var, var) for var in PAYMENT_STATUSES[2:-1]]
    )
    date_open = models.DateField(auto_now=True)
    date_pay = models.DateField(blank=True, null=True)
    date_close = models.DateField(blank=True, null=True, editable=False)

    class Meta:
        managed = True
        db_table = 'Payments'

    def __str__(self):
        return f'{self.user.username} ({self.status}) {self.date_open}: ' \
               f'{self.soft.aggregate(models.Sum("price"))["price__sum"]} ₽'


@receiver(post_save, sender=Payment)
def save_payment(sender, instance, *args, **kwargs):  # Could be made inside by usual create
    id = instance.id
    payment = Payment.objects.filter(id=id)

    # Setting date_close and date_pay after status fixing:
    date_close = now().date() \
        if instance.status in (PAYMENT_STATUSES[-1], PAYMENT_STATUSES[-2]) \
        else None
    date_pay = now().date() if instance.status == 'paid' else None

    instance.date_close = date_close
    instance.date_pay = date_pay
    payment.update(date_pay=date_pay, date_close=date_close)

    # Setting payment code:
    if not instance.code:
        code = sha256(str(id).encode('utf-8')).hexdigest()[:10]
        payment.update(code=code)
        instance.code = code


# FileField.path is not correct when using upload_to during save
# (and pre_save?) method - it doesn't contain that dir in path.
# So we use post_save signal.
