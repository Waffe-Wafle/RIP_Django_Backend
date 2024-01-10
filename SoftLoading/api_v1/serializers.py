from rest_framework.serializers import ModelSerializer, Serializer,  SerializerMethodField
from SoftLoading.models import Soft, File, Payment


def short_field(value):
    return value[:34] + ('...' if len(value) > 34 else '')


class FilesSerialiser(ModelSerializer):
    class Meta:
        model = File
        read_only_fields = ['size']
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        if self.context['request'].method != 'POST':
            fields.pop('file', None)

        return fields


class SoftSerializer(ModelSerializer):
    #  Done like that to increase speed:
    def __init__(self, *args, **kwargs):
        self.short_variant = kwargs.pop('short_variant', False)
        super(SoftSerializer, self).__init__(*args, **kwargs)

        # While project building object context is empty and serializer instance is created for testing:
        if self.context.get('request'):
            dict = self.context['request'].resolver_match.url_name

            if 'detail' in dict:  # Not retrieve, retrieve is used in ModelViewSet!
                # read_only=True IS needed bc of put except of patch method!
                self.fields['files'] = FilesSerialiser(many=True, source='file_set', read_only=True)
            self.short_variant = self.short_variant or any(variant in dict for variant in ['list', 'update', 'create'])

    def to_representation(self, instance):
        # Shorting some fields:
        data = super().to_representation(instance)
        descr = data['description']
        name = data['name']
        if self.short_variant:
            data['description'] = short_field(descr)
            data['name'] = short_field(name)
        return data

    class Meta:
        model = Soft
        fields = ['id', 'name', 'image', 'description', 'price']


class PaymentSerializer(ModelSerializer):
    price = SerializerMethodField()

    def get_price(self, obj):
        return sum(soft_obj.price for soft_obj in obj.soft.all())

    def __init__(self, *args, **kwargs):
        super(PaymentSerializer, self).__init__(*args, **kwargs)

        if self.context.get('request'):
            dict = self.context['request'].resolver_match.url_name
            if (self.context['request'].method in ['DELETE', 'PUT']) or (dict and 'detail' in dict):
                self.fields['soft'] = SoftSerializer(many=True, short_variant=True)

    class Meta:
        model = Payment
        read_only_fields = ['date_open', 'date_close',  'user', 'code']
        fields = '__all__'

