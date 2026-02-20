# core/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('times/', views.lista_times, name='lista_times'),
    path('times/<int:time_id>/', views.detalhe_time, name='detalhe_time'),
    path('jogos/', views.lista_jogos, name='lista_jogos'),
    path('proximos-jogos/', views.proximos_jogos, name='proximos_jogos'),
    path('tabela/', views.tabela, name='tabela'),
    path('artilharia/', views.artilharia, name='artilharia'),  # NOVA URL
    path('', views.lista_times, name='home'),
]