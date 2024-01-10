from django.core.validators import ValidationError


PAYMENT_STATUSES = ['opened', 'paid', 'rejected', 'completed', 'deleted']


def payment_status_validate(value):
    if value not in PAYMENT_STATUSES:
        raise ValidationError(f'Status should be one of {PAYMENT_STATUSES}')


SOFT_STATUSES = ['available', 'deleted']


def soft_status_validate(value):
    if value not in SOFT_STATUSES:
        raise ValidationError(f'Status shoulde be one of {PAYMENT_STATUSES}')


PLATFORMS = ['Windows', 'Linux', 'MacOS']


def file_platform_validate(value):
    if value not in PLATFORMS:
        raise ValidationError(f'Platform shoulde be one of {PLATFORMS}')


ARCHITECTURES = ['x32', 'x64']


def file_architecture_validate(value):
    if value not in ARCHITECTURES:
        raise ValidationError(f'Architecture shoulde be one of {PLATFORMS}')