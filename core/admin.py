# core/admin.py

from django.contrib import admin
from .models import Time, Jogador, Jogo, Gol

class JogadorInline(admin.TabularInline):
    model = Jogador
    extra = 3
    fields = ['nome', 'numero', 'posicao', 'ativo']
    classes = ['collapse']
    verbose_name = "Jogador"
    verbose_name_plural = "Jogadores"

class GolInline(admin.TabularInline):
    model = Gol
    extra = 3
    fields = ['jogador', 'time', 'minuto', 'tipo', 'contra']
    classes = ['collapse']
    verbose_name = "Gol"
    verbose_name_plural = "Gols"
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "jogador" and request._obj_:
            kwargs["queryset"] = Jogador.objects.filter(time=request._obj_.time_casa) | Jogador.objects.filter(time=request._obj_.time_visitante)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'data_criacao']
    list_filter = ['data_criacao']
    search_fields = ['nome']
    inlines = [JogadorInline]
    list_per_page = 20
    
    fieldsets = (
        ('Informações do Time', {
            'fields': ('nome', 'logo', 'data_criacao'),
            'classes': ('wide',)
        }),
    )
    
    readonly_fields = ['data_criacao']


@admin.register(Jogador)
class JogadorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'time', 'numero', 'posicao', 'ativo']
    list_filter = ['time', 'posicao', 'ativo']
    search_fields = ['nome', 'time__nome']
    list_editable = ['ativo']
    list_per_page = 20
    
    fieldsets = (
        ('Informações do Jogador', {
            'fields': ('nome', 'time', 'numero', 'posicao', 'foto', 'data_nascimento', 'nacionalidade', 'ativo'),
            'classes': ('wide',)
        }),
    )


@admin.register(Jogo)
class JogoAdmin(admin.ModelAdmin):
    list_display = ['rodada', 'time_casa', 'gols_casa', 'gols_visitante', 'time_visitante', 'data_jogo', 'local', 'realizado']
    list_filter = ['realizado', 'rodada', 'data_jogo', 'time_casa', 'time_visitante']
    search_fields = ['time_casa__nome', 'time_visitante__nome']
    list_editable = ['gols_casa', 'gols_visitante', 'realizado']
    date_hierarchy = 'data_jogo'
    list_per_page = 20
    
    fieldsets = (
        ('Informações da Partida', {
            'fields': ('rodada', 'time_casa', 'time_visitante', 'gols_casa', 'gols_visitante', 'data_jogo', 'local', 'realizado'),
            'classes': ('wide',)
        }),
    )
    
    inlines = [GolInline]
    
    def get_form(self, request, obj=None, **kwargs):
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)
    
    actions = ['marcar_como_realizado', 'marcar_como_nao_realizado']
    
    def marcar_como_realizado(self, request, queryset):
        count = queryset.update(realizado=True)
        self.message_user(request, f"{count} jogo{'s' if count > 1 else ''} marcado{'s' if count > 1 else ''} como realizado{'s' if count > 1 else ''}.")
    marcar_como_realizado.short_description = "Marcar como realizados"
    
    def marcar_como_nao_realizado(self, request, queryset):
        count = queryset.update(realizado=False)
        self.message_user(request, f"{count} jogo{'s' if count > 1 else ''} marcado{'s' if count > 1 else ''} como não realizado{'s' if count > 1 else ''}.")
    marcar_como_nao_realizado.short_description = "Marcar como não realizados"


@admin.register(Gol)
class GolAdmin(admin.ModelAdmin):
    list_display = ['jogador', 'time', 'jogo', 'minuto', 'tipo', 'contra']
    list_filter = ['time', 'tipo', 'contra', 'jogo__rodada']
    search_fields = ['jogador__nome', 'time__nome']
    list_per_page = 20
    
    fieldsets = (
        ('Informações do Gol', {
            'fields': ('jogo', 'jogador', 'time', 'minuto', 'tipo', 'contra'),
            'classes': ('wide',)
        }),
    )