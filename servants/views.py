from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Servant

def roster_view(request):
    query = request.GET.get('search', '').strip()
    class_filter = request.GET.get('class', '').strip()

    servants = Servant.objects.all().order_by('collection_no')

    if query:
        servants = servants.filter(name__icontains=query)
    
    if class_filter:
        servants = servants.filter(class_name__iexact=class_filter)

    # 24 cards per page keeps loading snappy on mobile and desktop
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
        'classes': classes,
    }
    return render(request, 'servants/roster.html', context)