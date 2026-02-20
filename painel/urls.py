# painel/urls.py

from django.urls import path
from . import views

app_name = 'painel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Times
    path('times/', views.lista_times, name='lista_times'),
    path('times/cadastrar/', views.cadastrar_time, name='cadastrar_time'),
    path('times/<int:time_id>/', views.detalhe_time, name='detalhe_time'),
    path('times/<int:time_id>/editar/', views.editar_time, name='editar_time'),
    path('times/<int:time_id>/excluir/', views.excluir_time, name='excluir_time'),
    
    # Jogadores
    path('jogadores/', views.lista_jogadores, name='lista_jogadores'),
    path('jogadores/cadastrar/', views.cadastrar_jogador, name='cadastrar_jogador'),
    path('jogadores/<int:jogador_id>/editar/', views.editar_jogador, name='editar_jogador'),
    path('jogadores/<int:jogador_id>/excluir/', views.excluir_jogador, name='excluir_jogador'),
    
    # Jogos
    path('jogos/', views.lista_jogos, name='lista_jogos'),
    path('jogos/cadastrar/', views.cadastrar_jogo, name='cadastrar_jogo'),
    path('jogos/<int:jogo_id>/editar/', views.editar_jogo, name='editar_jogo'),
    path('jogos/<int:jogo_id>/excluir/', views.excluir_jogo, name='excluir_jogo'),
    path('jogos/<int:jogo_id>/lancar/', views.lancar_resultado, name='lancar_resultado'),
    
    # ===== NOVAS URLs PARA GOLS =====
    # Gols
    path('gols/', views.lista_gols, name='lista_gols'),
    path('gols/cadastrar/', views.cadastrar_gol, name='cadastrar_gol'),
    path('gols/<int:gol_id>/editar/', views.editar_gol, name='editar_gol'),
    path('gols/<int:gol_id>/excluir/', views.excluir_gol, name='excluir_gol'),
    
    # AJAX (para carregar jogadores dinamicamente)
    path('ajax/carregar-jogadores/', views.carregar_jogadores_por_time, name='carregar_jogadores'),
]