from django.urls import path
from . import views

urlpatterns = [
    path('', views.map_view, name='regions.map'),
    path('api/states/', views.states_list_api, name='regions.states_api'),
    path('api/state/<int:state_id>/movies/', views.state_movies_api, name='regions.state_movies_api'),
    path('api/trending/', views.global_trending_api, name='regions.global_trending_api'),
    path('api/compare/', views.compare_states_api, name='regions.compare_api'),
    path('api/personal/', views.personal_purchases_api, name='regions.personal_api'),
    path('api/other-users/', views.other_users_api, name='regions.other_users_api'),
    path('api/compare-personal/', views.compare_personal_state_api, name='regions.compare_personal_api'),
]
