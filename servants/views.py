import requests
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Servant


def detail_view(request, collection_no):
    servant = get_object_or_404(Servant, collection_no=collection_no)

    force_refresh = request.GET.get('refresh_lore') == '1'
    has_valid_lore = (
        isinstance(servant.profile_lore, list)
        and len(servant.profile_lore) > 0
        and isinstance(servant.profile_lore[0], dict)
        and "comment" in servant.profile_lore[0]
        and not force_refresh
    )

    if not has_valid_lore:
        try:
            # 1. Resolve internal Atlas Spirit Origin ID via collection query
            search_url = f"https://api.atlasacademy.io/basic/NA/servant/search?collectionNo={servant.collection_no}"
            search_res = requests.get(search_url, timeout=6)
            
            target_id = None
            if search_res.status_code == 200 and search_res.json():
                target_id = search_res.json()[0].get("id")

            # 2. Fetch full lore profile using the resolved ID
            if target_id:
                lore_url = f"https://api.atlasacademy.io/nice/NA/servant/{target_id}?lore=true"
                lore_res = requests.get(lore_url, timeout=6)

                if lore_res.status_code == 200:
                    data = lore_res.json()
                    raw_comments = data.get("profile", {}).get("comments", [])

                    parsed_lore = []
                    for item in raw_comments:
                        cmt = item.get("comment", "").strip()
                        ttl = item.get("title", "CLASSIFIED ARCHIVE").strip()
                        if cmt:
                            parsed_lore.append({
                                "title": ttl,
                                "comment": cmt
                            })

                    if parsed_lore:
                        servant.profile_lore = parsed_lore
                        servant.save(update_fields=["profile_lore"])
        except Exception as e:
            print(f"Lore acquisition failed for #{servant.collection_no}: {e}")

    return render(request, 'servants/detail.html', {'servant': servant})

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