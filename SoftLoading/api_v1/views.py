from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from django.http import FileResponse

from SoftLoading.models import Soft, File, Payment
from django.db.models import Q, Sum
from .serializers import SoftSerializer, FilesSerialiser, PaymentSerializer
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from SoftLoading.validators import SOFT_STATUSES, PAYMENT_STATUSES
from datetime import datetime

from Site.settings import MINIO, AWS_STORAGE_BUCKET_NAME
from pathlib import Path
from minio.error import S3Error

from SoftLoading.user_singleton import UserSingleton


def add_count_option(instance, request: Request):
    if request.GET.get('count') == 'true':
        queryset = instance.get_queryset()
        return Response({'count': queryset.count()})


def get_model_obj(model, pk, force_empty=False):
    obj = model.objects.filter(id=pk).first()
    if not obj and not force_empty:
        raise NotFound({'detail': 'object not found'})
    return obj


def get_draft(request):
    return Payment.objects.filter(user=UserSingleton(), status=PAYMENT_STATUSES[0]).first()


class SoftViewSet(ModelViewSet):
    serializer_class = SoftSerializer
    queryset = Soft.objects.none()

    http_method_names = ['get', 'post', 'delete', 'put']

    def get_queryset(self):
        soft = Soft.objects.filter(status=SOFT_STATUSES[0])

        # Processing search:
        search = self.request.GET.get('search')
        if search:
            soft = soft.filter(
                Q(name__icontains=search) | Q(description__icontains=search) |
                (Q(price=search) if search.isnumeric() else Q(pk__in=[])) |
                Q(file__platform__icontains=search)
            ).distinct()  # Last query can put few same result

        # Processing price filter:
        match self.request.GET.get('cheap'):
            case 'up':
                soft = soft.order_by('price')
            case 'down':
                soft = soft.order_by('-price')

        # Processing price range filter:
        cheap_start = self.request.GET.get('cheap_start')
        if cheap_start:
            soft = soft.filter(price__gte=cheap_start)

        cheap_end = self.request.GET.get('cheap_end')
        if cheap_end:
            soft = soft.filter(price__lte=cheap_end)

        return soft

    def list(self, request: Request, *args, **kwargs):
        result = add_count_option(self, request)
        if result:
            return result

        draft = get_draft(request)
        data = self.serializer_class(self.get_queryset(), many=True,
                                     context={'request': request}).data
        return Response({
            'draft_id': draft.id if draft else None,
            'soft_list': data
        })

    def destroy(self, request: Request,  *args, **kwargs):
        soft = get_model_obj(Soft, kwargs.get('pk'))
        if soft.status == SOFT_STATUSES[-1]:
            raise NotFound({'detail': 'this soft already deleted'})

        soft.status = SOFT_STATUSES[-1]
        soft.save()
        return Response(status=204)


def validate_date(date: str, field: str):
    try:
        return datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ValidationError({'detail': field + ' field date format is incorrect.'})


# Getting and logically deleting payments:
class PaymentViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.none()
    http_method_names = ['get', 'delete']

    def get_queryset(self):
        payments = Payment.objects.all().exclude(status__in=[PAYMENT_STATUSES[0], PAYMENT_STATUSES[-1]])

        # Filters:
        code = self.request.GET.get('code')
        if code:
            payments = payments.filter(code=code)

        start = self.request.GET.get('start_date')
        if start:
            payments = payments.filter(date_open__gte=validate_date(start, 'start_date'))

        end = self.request.GET.get('end_date')
        if end:
            payments = payments.filter(date_open__lte=validate_date(end, 'end_date'))

        status = self.request.GET.get('status')
        if status:
            if status not in PAYMENT_STATUSES:
                raise ValidationError({'detail': 'wrong status specified'})
            payments = payments.filter(status=status)

        return payments

    def list(self, request: Request, *args, **kwargs):
        result = add_count_option(self, request)
        if result:
            return result

        # Ability to check summ of all payments matching query:
        if request.GET.get('sum') == 'true':
            return Response({
                'today_requested':
                    self.get_queryset().aggregate(summ_req=Sum('soft__price'))['summ_req']
            })

        return super().list(request, args, kwargs)

    def retrieve(self, request, *args, **kwargs):
        payment = get_model_obj(Payment, kwargs.get('pk'))  # Because get_queryset takes opened away
        if payment.status == PAYMENT_STATUSES[-1]:
            raise NotFound({'detail': 'payment not found'})

        return Response(self.get_serializer(payment).data)

    def destroy(self, request: Request, *args, **kwargs):
        payment = get_model_obj(Payment, kwargs.get('pk'))  # Same

        # Not to allow to user to delete other users payments:
        if payment.user != UserSingleton():
            raise PermissionDenied()

        if payment.status == PAYMENT_STATUSES[-1]:
            raise NotFound({'detail': 'this payment already deleted'})

        payment.status = PAYMENT_STATUSES[-1]
        payment.save()
        return Response(status=204)


# Manging status of payment for admin:
class PaymentStatusAdminView(APIView):

    def put(self, request, *args, **kwargs):
        payment = get_model_obj(Payment, kwargs.get('pk'))

        if payment.status == PAYMENT_STATUSES[-1]:
            raise NotFound({'detail': 'there is no such payment'})

        if payment.status != PAYMENT_STATUSES[1]:
            raise PermissionDenied({'detail': 'you cant change status now'})

        status = request.data.get('status')
        if status not in [PAYMENT_STATUSES[-3], PAYMENT_STATUSES[-2]]:
            raise PermissionDenied({'detail': 'wrong status specified'})

        payment.manager = UserSingleton()
        payment.status = status
        payment.save()

        return Response(PaymentSerializer(payment).data)


# Manging status of payment for user:
class PaymentStatusUserView(APIView):
    def put(self, request, *args, **kwargs):
        payment = get_draft(request)
        if not payment:
            raise NotFound({'detail': 'draft not found'})

        payment.status = PAYMENT_STATUSES[1]
        payment.save()
        return Response(PaymentSerializer(payment).data)


# Soft inside draft managing:
class PaymentSoftView(APIView):
    def put(self, request, *args, **kwargs):
        payment = get_draft(request)
        soft = get_model_obj(Soft, request.data.get('soft'))

        # Creating draft if needed:
        if not payment:
            payment = Payment.objects.create(user=UserSingleton(), status=PAYMENT_STATUSES[0])

        # Adding soft if not already added:
        if not payment.soft.filter(id=soft.id).exists():
            payment.soft.add(soft)

        return Response(PaymentSerializer(payment, context={'request': request}).data)

    def delete(self, request, *args, **kwargs):
        payment = get_draft(request)
        if not payment:
            raise NotFound({'detail': 'draft not found'})

        soft = get_model_obj(Soft, request.data.get('soft'), force_empty=True)
        payment.soft.remove(soft)

        return Response(PaymentSerializer(payment, context={'request': request}).data)


class FileViewSet(ModelViewSet):
    serializer_class = FilesSerialiser
    queryset = File.objects.all()

    http_method_names = ['get', 'post', 'delete']

    def retrieve(self, request, *args, **kwargs):
        try:
            file = File.objects.get(id=self.kwargs.get('pk'))

            # Получаем имя файла и object name из модели File
            filename = f'{file.soft.name.replace(" ", "_")}_' \
                       f'{file.platform.replace(" ", "_")}_' \
                       f'{file.architecture}.' \
                       f'{Path(file.file.name).suffix.replace(".", "")}'  # Расширение файла
            object_name = file.file.name  # Путь к файлу в Minio

            return FileResponse(MINIO.get_object(AWS_STORAGE_BUCKET_NAME, object_name),
                                filename=filename,
                                as_attachment=True)

        except (File.DoesNotExist, S3Error):
            raise NotFound({'detail': 'there is no specified file'})

