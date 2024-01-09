from django.http import HttpRequest
from django.shortcuts import render
# from SoftLoading.models import *
# from django.db.models import Q
# from datetime import date
import psycopg2
from Site.settings import CONFIG


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
print(results)


# For lab 1:
def filter_softs(softs, search):
    filtered_softs = []
    for soft in softs:
        if (
                search.lower() in soft['name'].lower() or
                (search.isdigit() and int(search) == soft['price'])
        ): filtered_softs.append(soft)

    return filtered_softs


def range_softs_by_orice(softs, ascending=True):
    sorted_softs = sorted(softs, key=lambda x: x['price'], reverse=not ascending)
    return sorted_softs


SOFTS = [
    {'id': 0,
     'name': 'Libre Office',
     'image': 'https://wifitel.ru/images/wp-content/uploads/2020/05/ris.-1-libre-ofis-vvedenie.jpg',
     'description': 'LibreOffice - это бесплатный и открытый офисный пакет программного обеспечения, '
                    'предоставляющий набор приложений для офисной работы.',
     'price': 202,
     'files': [
         {'id': 0,
          'soft_id': 0,
          'file': '',
          'size': '',
          'platform': '',
          'architecture': ''},
         {'id': 1,
          'soft_id': 0,
          'file': '',
          'size': '',
          'platform': '',
          'architecture': ''},
     ]},
    {'id': 1,
     'name': 'Microsoft Office Acces 2016',
     'image': 'https://visiontrainingsystems.com/wp-content/uploads/2016/05/access-2016.png',
     'description': 'Система управления базами данных, предназначенная для создания и обработки баз данных.',
     'price': 150,
     'files': []},
    {'id': 3,
     'name': 'Microsoft Office Exel 2016',
     'image': 'https://adhambek2303.files.wordpress.com/2022/05/excel_video_glavnaya.png',
     'description': 'Программа для создания электронных таблиц, проведения расчетов, анализа данных и '
                    'построения графиков, предоставляющая инструменты для эффективной работы с числовой '
                    'информацией.',
     'price': 230,
     'files': []},
    {'id': 4,
     'name': 'Microsoft Office Word 2016',
     'image': 'https://bringwell.ru/wp-content/uploads/7/f/4/7f4939ed06279ae45b21c93b0bb2f353.png',
     'description': 'Стандартная программа из офисного пакета от компании Microsoft. '
                    'Является мощным текстовым редактором для создания и форматирования документов различных '
                    'типов, включая письма, отчеты, и научные работы.',
     'price': 250,
     'files': []},
]


# For all:
def get_soft_data(soft, files=False):
    data = soft
    if not files:
        data.update({'description': soft['description']})
        data['description'] = data['description'][:34] + '...'
        del data['files']

    # For orm:
    # data = {
    #     'id': soft.id, 'name': soft.name,
    #     'image': soft.image,
    #     'price': soft.price,
    # }
    # if files:
    #     data.update({'description': soft.description})
    #     data.update({'files': files})

    return data

MOCK_SOFTS = [
    {'id': 0,
     'name': 'Libre Office',
     'image': 'https://wifitel.ru/images/wp-content/uploads/2020/05/ris.-1-libre-ofis-vvedenie.jpg',
     'description': 'LibreOffice - это бесплатный и открытый офисный пакет программного обеспечения, '
                    'предоставляющий набор приложений для офисной работы.',
     'price': 202,
     'files': [
         {'id': 0,
          'soft_id': 0,
          'file': 'https://download.documentfoundation.org/libreoffice/stable/7.6.4/rpm/x86_64/LibreOffice_7.6.4_Linux_x86-64_rpm.tar.gz',
          'size': '240 Мб',
          'platform': 'Linux',
          'architecture': 'x32'},
         {'id': 1,
          'soft_id': 0,
          'file': 'https://download.documentfoundation.org/libreoffice/stable/7.6.4/win/x86_64/LibreOffice_7.6.4_Win_x86-64.msi',
          'size': '245 Мб',
          'platform': 'Windows',
          'architecture': 'x32'},
     ]},
    {'id': 1,
     'name': 'Microsoft Office Acces 2016',
     'image': 'https://visiontrainingsystems.com/wp-content/uploads/2016/05/access-2016.png',
     'description': 'Система управления базами данных, предназначенная для создания и обработки баз данных.',
     'price': 150,
     'files': []},
    {'id': 2,
     'name': 'Microsoft Office Exel 2016',
     'image': 'https://adhambek2303.files.wordpress.com/2022/05/excel_video_glavnaya.png',
     'description': 'Программа для создания электронных таблиц, проведения расчетов, анализа данных и '
                    'построения графиков, предоставляющая инструменты для эффективной работы с числовой '
                    'информацией.',
     'price': 230,
     'files': []},
    {'id': 3,
     'name': 'Microsoft Office Word 2016',
     'image': 'https://bringwell.ru/wp-content/uploads/7/f/4/7f4939ed06279ae45b21c93b0bb2f353.png',
     'description': 'Стандартная программа из офисного пакета от компании Microsoft. '
                    'Является мощным текстовым редактором для создания и форматирования документов различных '
                    'типов, включая письма, отчеты, и научные работы.',
     'price': 250,
     'files': []},
]

def catalog(request: HttpRequest):
    # Processing deleting for lab 2:
    # soft_id = request.POST.get('delete')
    # if soft_id:
    #     with con.cursor() as curs:
    #         curs.execute(f'DELETE FROM "Soft" WHERE id = {soft_id}')
    #     print('Deletion done,', soft_id)

    nonlocal SOFTS
    softsL = dict(SOFTS)

    search = request.POST.get('search')
    if search:
        softsL = filter_softs(softsL, search)

    filter = request.POST.get('filter')
    match filter:
        case 'up':
            softsL = range_softs_by_orice(softsL, ascending=True)
        case 'down':
            softsL = range_softs_by_orice(softsL, ascending=False)

    # # After lab 1
    # SOFTS = Soft.objects.all()
    #
    # # Processing search and filter:
    # search = request.POST.get('search')
    # if search:
    #     softs = softs.filter(
    #         Q(name__icontains=search) | Q(description__icontains=search) |
    #         (Q(price=search) if search.isnumeric() else Q(pk__in=[])) |
    #         Q(file__platform__icontains=search)
    #     ).distinct()
    #
    # filter = request.POST.get('filter')
    # match filter:
    #     case 'up':
    #         SOFTS = SOFTS.order_by('price')
    #     case 'down':
    #         SOFTS = SOFTS.order_by('-price')

    # Amount condition:
    try:
        softsL = softsL[:int(request.POST.get('amount'))]
    except:
        pass

    soft_list = [get_soft_data(soft) for soft in softsL]

    return render(request, 'SoftLoading/catalog.html', {'soft_list': soft_list,
                                                        'search_text': search,
                                                        'filter': filter})


def soft(request, soft_id):
    _soft = get_soft_data(
        # Soft.objects.get(id=soft_id), files=File.objects.filter(soft_id=soft_id)
        SOFTS[0]
    )

    return render(request, 'SoftLoading/soft.html', {'soft': _soft})
