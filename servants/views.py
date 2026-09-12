from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Servant

def detail_view(request, collection_no):
    servant = get_object_or_404(Servant, collection_no=collection_no)
    
    context = {
        'servant': servant,
    }
    return render(request, 'servants/detail.html', context)

def roster_view(request):
    query = request.GET.get('search', '').strip()
    class_filter = request.GET.get('class', '').strip()
    rarity_filter = request.GET.get('rarity', '').strip()
    sort_option = request.GET.get('sort', 'collection_asc').strip()

    servants = Servant.objects.all()

    # Text Search (Name)
    if query:
        servants = servants.filter(name__icontains=query)
    
    # Class Filter
    if class_filter:
        servants = servants.filter(class_name__iexact=class_filter)

    # Rarity (Stars) Filter
    if rarity_filter and rarity_filter.isdigit():
        servants = servants.filter(rarity=int(rarity_filter))

    # Sorting Map
    sort_map = {
        'collection_asc': 'collection_no',
        'collection_desc': '-collection_no',
        'atk_desc': '-atk_max',
        'atk_asc': 'atk_max',
        'hp_desc': '-hp_max',
        'hp_asc': 'hp_max',
        'rarity_desc': '-rarity',
        'rarity_asc': 'rarity',
    }
    order_field = sort_map.get(sort_option, 'collection_no')
    servants = servants.order_by(order_field)

    # Pagination: 24 per page
    paginator = Paginator(servants, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    classes = [
        'Saber', 'Archer', 'Lancer', 'Rider', 'Caster', 
        'Assassin', 'Berserker', 'Ruler', 'Avenger', 'Alterego', 'Pretender'
    ]

    context = {
        'page_obj': page_obj,
        'search_query': query,
        'selected_class': class_filter,
        'selected_rarity': rarity_filter,
        'selected_sort': sort_option,
        'classes': classes,
        'rarities': [5, 4, 3, 2, 1],
    }
    return render(request, 'servants/roster.html', context)

# servants/views.py

def compare_view(request):
    servant_a_id = request.GET.get('servant_a')
    servant_b_id = request.GET.get('servant_b')

    # Query only the lightweight fields needed for the dropdowns
    servant_options = Servant.objects.all().only('collection_no', 'name', 'class_name').order_by('collection_no')

    servant_a = None
    servant_b = None

    if servant_a_id and servant_a_id.isdigit():
        servant_a = Servant.objects.filter(collection_no=int(servant_a_id)).first()

    if servant_b_id and servant_b_id.isdigit():
        servant_b = Servant.objects.filter(collection_no=int(servant_b_id)).first()

    diff = {}
    if servant_a and servant_b:
        diff = {
            'atk_diff': servant_a.atk_max - servant_b.atk_max,
            'hp_diff': servant_a.hp_max - servant_b.hp_max,
            'cost_diff': servant_a.cost - servant_b.cost,
        }

    context = {
        'servant_options': servant_options,
        'servant_a': servant_a,
        'servant_b': servant_b,
        'diff': diff,
    }
    return render(request, 'servants/compare.html', context)

def about_view(request):
    return render(request, 'servants/about.html')