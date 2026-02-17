"""URL Configuration"""
from django.urls import path
from auction import views

urlpatterns = [
    path('api/populate/', views.populate_data, name='populate_data'),
    path('api/players/', views.player_list, name='player_list'),
    path('api/players/active/', views.active_player, name='active_player'),
    path('api/players/<int:pk>/bid/', views.place_bid, name='place_bid'),
    path('api/teams/', views.team_list, name='team_list'),
]
