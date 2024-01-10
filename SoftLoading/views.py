from django.http import HttpRequest
from django.shortcuts import render
from SoftLoading.models import *
from django.db.models import Q
import psycopg2
from Site.settings import CONFIG
from SoftLoading.validators import SOFT_STATUSES


con = psycopg2.connect(
    database=CONFIG.get('Postgres DB', 'name'),
    user=CONFIG.get('Postgres DB', 'user'),
    password=CONFIG.get('Postgres DB', 'password'),
    host=CONFIG.get('Postgres DB', 'host'),
    port=CONFIG.get('Postgres DB', 'port')
)
con.set_isolation_level(0)


cur = con.cursor()
cur.execute('SELECT * FROM "Payments"')
results = cur.fetchall()
print('Payments:')
[print(paiment) for paiment in results]
print()

cur.execute('SELECT * FROM "Soft"')
results = cur.fetchall()
print('Soft:')
[print(soft) for soft in results]


def short_field(value):
    return value[:34] + ('...' if len(value) > 34 else '')


def get_soft_data(soft, extended=False, files=None):
    data = {
        'id': soft.id,
        'name': soft.name if extended else short_field(soft.name) ,
        'image': soft.image.url if soft.image else None,
        'price': soft.price,
        'description': soft.description  if extended else short_field(soft.description)
    }
    if extended:
        data.update({'files': files})

    return data


def catalog(request: HttpRequest):
    # Processing deleting:
    soft_id = request.POST.get('delete')
    if soft_id:
        with con.cursor() as curs:
            curs.execute(f"UPDATE \"Soft\" SET status='{SOFT_STATUSES[-1]}' WHERE id = {soft_id}")
        print('Deletion done,', soft_id)

    softs = Soft.objects.filter(status=SOFT_STATUSES[0])

    # Processing search and filter:
    search = request.POST.get('search')
    if search:
        softs = softs.filter(
            Q(name__icontains=search) | Q(description__icontains=search) |
            (Q(price=search) if search.isnumeric() else Q(pk__in=[])) |
            Q(file__platform__icontains=search)
        ).distinct()

    filter = request.POST.get('filter')
    match filter:
        case 'up':
            softs = softs.order_by('price')
        case 'down':
            softs = softs.order_by('-price')

    # Amount condition:
    try:
        softs = softs[:int(request.POST.get('amount'))]
    except:
        pass

    soft_list = [get_soft_data(soft) for soft in softs]

    return render(request, 'SoftLoading/catalog.html', {'soft_list': soft_list,
                                                        'search_text': search if search else '',
                                                        'filter': filter})


def soft(request, soft_id):
    soft = get_soft_data(
        Soft.objects.get(id=soft_id), extended=True, files=File.objects.filter(soft_id=soft_id),
    )
    return render(request, 'SoftLoading/soft.html', {'soft': soft})
