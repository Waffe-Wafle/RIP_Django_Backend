from django.http import HttpRequest
from django.shortcuts import render
from copy import deepcopy


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


# For all:
def get_soft_data(soft, files=False):
    if not files:
        soft['description'] = soft['description'][:34] + '...'
        del soft['files']
    return soft


def catalog(request: HttpRequest):
    softsL = deepcopy(MOCK_SOFTS)

    # Searching:
    search = request.POST.get('search')
    if search:
        softsL = filter_softs(softsL, search)

    # Filtering:
    filter = request.POST.get('filter')
    match filter:
        case 'up':
            softsL = range_softs_by_orice(softsL, ascending=True)
        case 'down':
            softsL = range_softs_by_orice(softsL, ascending=False)

    # Amount condition:
    try:
        softsL = softsL[:int(request.POST.get('amount'))]
    except:
        pass

    # Adapting for view:
    soft_list = [get_soft_data(soft) for soft in softsL]

    return render(request, 'SoftLoading/catalog.html', {'soft_list': soft_list,
                                                        'search_text': search,
                                                        'filter': filter})


def soft(request, soft_id):
    soft = get_soft_data(deepcopy(MOCK_SOFTS[soft_id]), files=True)
    return render(request, 'SoftLoading/soft.html', {'soft': soft})
