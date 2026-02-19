# core/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Time, Jogo
from django.utils import timezone

def lista_times(request):
    times = Time.objects.all()
    dados_times = []
    
    for time in times:
        # Buscar todos os jogos do time (apenas realizados)
        jogos_casa = Jogo.objects.filter(time_casa=time, realizado=True)
        jogos_visitante = Jogo.objects.filter(time_visitante=time, realizado=True)
        
        # Inicializar contadores
        pontos = 0
        jogos_disputados = 0
        vitorias = 0
        empates = 0
        derrotas = 0
        gols_pro = 0
        gols_contra = 0
        
        # Jogos como casa
        for jogo in jogos_casa:
            gols_pro += jogo.gols_casa
            gols_contra += jogo.gols_visitante
            jogos_disputados += 1
            
            if jogo.gols_casa > jogo.gols_visitante:
                vitorias += 1
                pontos += 3
            elif jogo.gols_casa == jogo.gols_visitante:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        # Jogos como visitante
        for jogo in jogos_visitante:
            gols_pro += jogo.gols_visitante
            gols_contra += jogo.gols_casa
            jogos_disputados += 1
            
            if jogo.gols_visitante > jogo.gols_casa:
                vitorias += 1
                pontos += 3
            elif jogo.gols_visitante == jogo.gols_casa:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        saldo_gols = gols_pro - gols_contra
        
        dados_times.append({
            'time': time,
            'pontos': pontos,
            'jogos': jogos_disputados,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'saldo_gols': saldo_gols,
        })
    
    # Ordenar por ordem alfabética
    dados_times.sort(key=lambda x: x['time'].nome)
    
    return render(request, 'lista_times.html', {'dados_times': dados_times})


def detalhe_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    
    # Busca todos os jogos deste time
    jogos = Jogo.objects.filter(
        Q(time_casa=time) | Q(time_visitante=time)
    ).order_by('-data_jogo')
    
    jogos_realizados = jogos.filter(realizado=True)
    jogos_futuros = jogos.filter(realizado=False, data_jogo__gte=timezone.now())
    
    # Calcula estatísticas do time
    estatisticas = {
        'jogos': jogos_realizados.count(),
        'vitorias': 0,
        'empates': 0,
        'derrotas': 0,
        'gols_pro': 0,
        'gols_contra': 0,
    }
    
    for jogo in jogos_realizados:
        if jogo.time_casa == time:
            estatisticas['gols_pro'] += jogo.gols_casa
            estatisticas['gols_contra'] += jogo.gols_visitante
            if jogo.gols_casa > jogo.gols_visitante:
                estatisticas['vitorias'] += 1
            elif jogo.gols_casa == jogo.gols_visitante:
                estatisticas['empates'] += 1
            else:
                estatisticas['derrotas'] += 1
        else:  # time é visitante
            estatisticas['gols_pro'] += jogo.gols_visitante
            estatisticas['gols_contra'] += jogo.gols_casa
            if jogo.gols_visitante > jogo.gols_casa:
                estatisticas['vitorias'] += 1
            elif jogo.gols_visitante == jogo.gols_casa:
                estatisticas['empates'] += 1
            else:
                estatisticas['derrotas'] += 1
    
    estatisticas['saldo_gols'] = estatisticas['gols_pro'] - estatisticas['gols_contra']
    
    if estatisticas['jogos'] > 0:
        pontos = (estatisticas['vitorias'] * 3) + estatisticas['empates']
        estatisticas['aproveitamento'] = round((pontos / (estatisticas['jogos'] * 3)) * 100, 1)
    else:
        estatisticas['aproveitamento'] = 0
    
    context = {
        'time': time,
        'jogos_realizados': jogos_realizados[:5],
        'jogos_futuros': jogos_futuros[:5],
        'estatisticas': estatisticas,
    }
    
    return render(request, 'detalhe_time.html', context)


def lista_jogos(request):
    # Busca jogos realizados e ordena por rodada
    jogos = Jogo.objects.filter(realizado=True).order_by('rodada', '-data_jogo')
    return render(request, 'lista_jogos.html', {'jogos': jogos})


def tabela(request):
    times = Time.objects.all()
    dados_times = []
    
    for time in times:
        # Buscar todos os jogos do time (apenas realizados)
        jogos_casa = Jogo.objects.filter(time_casa=time, realizado=True)
        jogos_visitante = Jogo.objects.filter(time_visitante=time, realizado=True)
        
        # Inicializar contadores
        pontos = 0
        jogos_disputados = 0
        vitorias = 0
        empates = 0
        derrotas = 0
        gols_pro = 0
        gols_contra = 0
        
        # Jogos como casa
        for jogo in jogos_casa:
            gols_pro += jogo.gols_casa
            gols_contra += jogo.gols_visitante
            jogos_disputados += 1
            
            if jogo.gols_casa > jogo.gols_visitante:
                vitorias += 1
                pontos += 3
            elif jogo.gols_casa == jogo.gols_visitante:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        # Jogos como visitante
        for jogo in jogos_visitante:
            gols_pro += jogo.gols_visitante
            gols_contra += jogo.gols_casa
            jogos_disputados += 1
            
            if jogo.gols_visitante > jogo.gols_casa:
                vitorias += 1
                pontos += 3
            elif jogo.gols_visitante == jogo.gols_casa:
                empates += 1
                pontos += 1
            else:
                derrotas += 1
        
        saldo_gols = gols_pro - gols_contra
        
        dados_times.append({
            'time': time,
            'pontos': pontos,
            'jogos': jogos_disputados,
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'gols_pro': gols_pro,
            'gols_contra': gols_contra,
            'saldo_gols': saldo_gols,
        })
    
    # Ordenar por pontos, depois vitórias, depois saldo, depois gols pro
    from operator import itemgetter
    dados_times.sort(key=itemgetter('pontos', 'vitorias', 'saldo_gols', 'gols_pro'), reverse=True)
    
    return render(request, 'tabela.html', {'dados_times': dados_times})


def proximos_jogos(request):
    # Buscar rodada da URL (se fornecida)
    rodada = request.GET.get('rodada')
    
    # Query base: jogos futuros não realizados
    jogos_base = Jogo.objects.filter(
        realizado=False,
        data_jogo__gte=timezone.now()
    )
    
    # Obter todas as rodadas disponíveis para o filtro
    todas_rodadas = Jogo.objects.filter(
        realizado=False,
        data_jogo__gte=timezone.now()
    ).values_list('rodada', flat=True).distinct().order_by('rodada')
    
    # Aplicar filtro por rodada se especificado
    if rodada:
        try:
            rodada_int = int(rodada)
            jogos_filtrados = jogos_base.filter(rodada=rodada_int).order_by('data_jogo')
            rodada_selecionada = rodada_int
        except ValueError:
            jogos_filtrados = jogos_base.order_by('rodada', 'data_jogo')
            rodada_selecionada = None
    else:
        jogos_filtrados = jogos_base.order_by('rodada', 'data_jogo')
        rodada_selecionada = None
    
    context = {
        'jogos': jogos_filtrados,
        'todas_rodadas': todas_rodadas,
        'rodada_selecionada': rodada_selecionada,
    }
    
    return render(request, 'proximos_jogos.html', context)