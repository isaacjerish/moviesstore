from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='petitions.index'),
    path('create/', views.create, name='petitions.create'),
    path('<int:id>/', views.show, name='petitions.show'),
    path('<int:id>/vote/', views.vote, name='petitions.vote'),
    path('my/', views.my_petitions, name='petitions.my'),
]
