# core/views.py

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from .models import Time, Jogador, Jogo, Gol
from django.utils import timezone

def lista_times(request):
    times = Time.objects.all()
    dados_times = []
    
    for time in times:
        jogos_casa = Jogo.objects.filter(time_casa=time, realizado=True)
        jogos_visitante = Jogo.objects.filter(time_visitante=time, realizado=True)
        
        pontos = 0
        jogos_disputados = 0
        vitorias = 0
        empates = 0
        derrotas = 0
        gols_pro = 0
        gols_contra = 0
        
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
    
    dados_times.sort(key=lambda x: x['time'].nome)
    
    return render(request, 'lista_times.html', {'dados_times': dados_times})


def detalhe_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    
    jogos = Jogo.objects.filter(
        Q(time_casa=time) | Q(time_visitante=time)
    ).order_by('-data_jogo')
    
    jogos_realizados = jogos.filter(realizado=True)
    jogos_futuros = jogos.filter(realizado=False, data_jogo__gte=timezone.now())
    
    jogadores = time.jogadores.filter(ativo=True).order_by('posicao', 'numero')
    
    goleiros = jogadores.filter(posicao='GOL')
    zagueiros = jogadores.filter(posicao='ZAG')
    laterais = jogadores.filter(posicao='LAT')
    volantes = jogadores.filter(posicao='VOL')
    meias = jogadores.filter(posicao='MEI')
    atacantes = jogadores.filter(posicao='ATA')
    tecnicos = jogadores.filter(posicao='TEC')
    
    artilheiros_time = Gol.objects.filter(
        time=time,
        contra=False
    ).values('jogador').annotate(
        total_gols=Count('id')
    ).order_by('-total_gols')[:5]
    
    artilheiros_lista = []
    for item in artilheiros_time:
        jogador = Jogador.objects.get(id=item['jogador'])
        artilheiros_lista.append({
            'jogador': jogador,
            'gols': item['total_gols']
        })
    
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
        else:
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
        'goleiros': goleiros,
        'zagueiros': zagueiros,
        'laterais': laterais,
        'volantes': volantes,
        'meias': meias,
        'atacantes': atacantes,
        'tecnicos': tecnicos,
        'artilheiros': artilheiros_lista,
    }
    
    return render(request, 'detalhe_time.html', context)


def lista_jogos(request):
    # Obter parâmetro de rodada da URL
    rodada = request.GET.get('rodada')
    
    # Query base: jogos realizados
    jogos = Jogo.objects.filter(realizado=True)
    
    # Obter todas as rodadas disponíveis para o filtro
    rodadas_disponiveis = Jogo.objects.filter(
        realizado=True
    ).values_list('rodada', flat=True).distinct().order_by('rodada')
    
    # Aplicar filtro por rodada se especificado
    if rodada and rodada != 'todas':
        try:
            rodada_int = int(rodada)
            jogos = jogos.filter(rodada=rodada_int)
            rodada_selecionada = rodada_int
        except ValueError:
            rodada_selecionada = None
    else:
        rodada_selecionada = None
    
    # Ordenar por data (mais recentes primeiro)
    jogos = jogos.order_by('-data_jogo')
    
    context = {
        'jogos': jogos,
        'rodadas_disponiveis': rodadas_disponiveis,
        'rodada_selecionada': rodada_selecionada,
    }
    
    return render(request, 'lista_jogos.html', context)


def tabela(request):
    times = Time.objects.all()
    dados_times = []
    
    for time in times:
        jogos_casa = Jogo.objects.filter(time_casa=time, realizado=True)
        jogos_visitante = Jogo.objects.filter(time_visitante=time, realizado=True)
        
        pontos = 0
        jogos_disputados = 0
        vitorias = 0
        empates = 0
        derrotas = 0
        gols_pro = 0
        gols_contra = 0
        
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
    
    from operator import itemgetter
    dados_times.sort(key=itemgetter('pontos', 'vitorias', 'saldo_gols', 'gols_pro'), reverse=True)
    
    return render(request, 'tabela.html', {'dados_times': dados_times})


def proximos_jogos(request):
    rodada = request.GET.get('rodada')
    
    jogos_base = Jogo.objects.filter(
        realizado=False,
        data_jogo__gte=timezone.now()
    )
    
    todas_rodadas = Jogo.objects.filter(
        realizado=False,
        data_jogo__gte=timezone.now()
    ).values_list('rodada', flat=True).distinct().order_by('rodada')
    
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


def artilharia(request):
    artilheiros = Gol.objects.filter(
        contra=False
    ).values('jogador').annotate(
        total_gols=Count('id')
    ).order_by('-total_gols')
    
    ranking = []
    for item in artilheiros:
        jogador = Jogador.objects.select_related('time').get(id=item['jogador'])
        ranking.append({
            'jogador': jogador,
            'gols': item['total_gols']
        })
    
    times_gols = Gol.objects.filter(
        contra=False
    ).values('time').annotate(
        total_gols=Count('id')
    ).order_by('-total_gols')
    
    times_ranking = []
    for item in times_gols:
        time = Time.objects.get(id=item['time'])
        times_ranking.append({
            'time': time,
            'gols': item['total_gols']
        })
    
    context = {
        'ranking': ranking,
        'times_ranking': times_ranking,
        'total_gols': Gol.objects.filter(contra=False).count(),
    }
    
    return render(request, 'artilharia.html', context)

def dashboard_usuario(request):
    # Estatísticas gerais
    total_times = Time.objects.count()
    total_jogadores = Jogador.objects.count()
    total_jogos = Jogo.objects.filter(realizado=True).count()
    total_gols = Gol.objects.filter(contra=False).count()
    
    # Últimos jogos
    ultimos_jogos = Jogo.objects.filter(realizado=True).order_by('-data_jogo')[:5]
    
    # Próximos jogos
    proximos_jogos = Jogo.objects.filter(realizado=False, data_jogo__gte=timezone.now()).order_by('data_jogo')[:5]
    
    # Top 5 artilheiros
    top_artilheiros = Gol.objects.filter(
        contra=False
    ).values('jogador').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    artilheiros_lista = []
    for item in top_artilheiros:
        jogador = Jogador.objects.select_related('time').get(id=item['jogador'])
        artilheiros_lista.append({
            'jogador': jogador,
            'gols': item['total']
        })
    
    # Classificação (top 5)
    times = Time.objects.all()
    classificacao = []
    
    for time in times:
        jogos_casa = Jogo.objects.filter(time_casa=time, realizado=True)
        jogos_visitante = Jogo.objects.filter(time_visitante=time, realizado=True)
        
        pontos = 0
        vitorias = 0
        gols_pro = 0
        gols_contra = 0
        
        for jogo in jogos_casa:
            gols_pro += jogo.gols_casa
            gols_contra += jogo.gols_visitante
            if jogo.gols_casa > jogo.gols_visitante:
                vitorias += 1
                pontos += 3
            elif jogo.gols_casa == jogo.gols_visitante:
                pontos += 1
        
        for jogo in jogos_visitante:
            gols_pro += jogo.gols_visitante
            gols_contra += jogo.gols_casa
            if jogo.gols_visitante > jogo.gols_casa:
                vitorias += 1
                pontos += 3
            elif jogo.gols_visitante == jogo.gols_casa:
                pontos += 1
        
        saldo_gols = gols_pro - gols_contra
        
        classificacao.append({
            'time': time,
            'pontos': pontos,
            'jogos': jogos_casa.count() + jogos_visitante.count(),
            'vitorias': vitorias,
            'saldo_gols': saldo_gols,
        })
    
    # Ordenar por pontos
    classificacao.sort(key=lambda x: x['pontos'], reverse=True)
    top_5_classificacao = classificacao[:5]
    
    context = {
        'total_times': total_times,
        'total_jogadores': total_jogadores,
        'total_jogos': total_jogos,
        'total_gols': total_gols,
        'ultimos_jogos': ultimos_jogos,
        'proximos_jogos': proximos_jogos,
        'artilheiros': artilheiros_lista,
        'classificacao': top_5_classificacao,
    }
    return render(request, 'dashboard_usuario.html', context)