from django.urls import path

from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.index, name='index'),
    path('load_data/', views.load_data, name='load_data'),
    path(
        'suggestion/<int:pk>/',
        views.check_suggestion,
        name='check_suggestion')
]
