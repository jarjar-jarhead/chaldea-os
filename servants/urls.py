from django.urls import path
from . import views

app_name = 'servants'

urlpatterns = [
    path('', views.roster_view, name='roster'),
    path('servants/<int:collection_no>/', views.detail_view, name='detail'),
]