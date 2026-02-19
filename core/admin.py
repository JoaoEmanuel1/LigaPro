# core/admin.py

from django.contrib import admin
from .models import Time, Jogo

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_criacao']
    search_fields = ['nome']
    list_per_page = 20
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'logo'),
            'classes': ('wide',)
        }),
        ('Controle', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['data_criacao']


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ['rodada', 'time_casa', 'gols_casa', 'gols_visitante', 'time_visitante', 'data_jogo', 'local', 'realizado']
    list_filter = ['realizado', 'rodada', 'data_jogo', 'time_casa', 'time_visitante']
    search_fields = ['time_casa__nome', 'time_visitante__nome']
    list_editable = ['gols_casa', 'gols_visitante', 'realizado']
    date_hierarchy = 'data_jogo'
    list_per_page = 20
    
    fieldsets = (
        ('Times', {
            'fields': ('time_casa', 'time_visitante'),
            'classes': ('wide',),
            'description': 'Selecione os times participantes'
        }),
        ('Resultado', {
            'fields': ('gols_casa', 'gols_visitante', 'realizado'),
            'classes': ('wide',),
            'description': 'Preencha apenas se o jogo já foi realizado'
        }),
        ('Informações do Jogo', {
            'fields': ('data_jogo', 'local', 'rodada'),
            'classes': ('wide',),
            'description': 'Data, horário, local e rodada da partida'
        }),
    )
    
    # Ações em massa
    actions = ['marcar_como_realizado', 'marcar_como_nao_realizado']
    
    def marcar_como_realizado(self, request, queryset):
        count = queryset.update(realizado=True)
        self.message_user(request, f"{count} jogo{'s' if count > 1 else ''} marcado{'s' if count > 1 else ''} como realizado{'s' if count > 1 else ''}.")
    marcar_como_realizado.short_description = "Marcar como realizados"
    
    def marcar_como_nao_realizado(self, request, queryset):
        count = queryset.update(realizado=False)
        self.message_user(request, f"{count} jogo{'s' if count > 1 else ''} marcado{'s' if count > 1 else ''} como não realizado{'s' if count > 1 else ''}.")
    marcar_como_nao_realizado.short_description = "Marcar como não realizados"