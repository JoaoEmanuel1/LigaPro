# painel/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from core.models import Time, Jogador, Jogo, Gol
from django.db.models import Count, Sum, Q

@staff_member_required
def dashboard(request):
    # Estatísticas gerais
    total_times = Time.objects.count()
    total_jogadores = Jogador.objects.count()
    total_jogos = Jogo.objects.count()
    total_gols = Gol.objects.filter(contra=False).count()
    
    # Jogos recentes
    jogos_recentes = Jogo.objects.filter(realizado=True).order_by('-data_jogo')[:5]
    
    # Próximos jogos
    proximos_jogos = Jogo.objects.filter(realizado=False, data_jogo__gte=timezone.now()).order_by('data_jogo')[:5]
    
    # Top artilheiros
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
    
    context = {
        'total_times': total_times,
        'total_jogadores': total_jogadores,
        'total_jogos': total_jogos,
        'total_gols': total_gols,
        'jogos_recentes': jogos_recentes,
        'proximos_jogos': proximos_jogos,
        'artilheiros': artilheiros_lista,
    }
    return render(request, 'painel/dashboard.html', context)


@staff_member_required
def lista_times(request):
    times = Time.objects.all().annotate(
        num_jogadores=Count('jogadores'),
        num_gols=Count('gols')
    ).order_by('nome')
    
    context = {
        'times': times,
    }
    return render(request, 'painel/times.html', context)


@staff_member_required
def detalhe_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    jogadores = time.jogadores.all().order_by('posicao', 'numero')
    
    context = {
        'time': time,
        'jogadores': jogadores,
    }
    return render(request, 'painel/detalhe_time.html', context)


@staff_member_required
def cadastrar_time(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        logo = request.FILES.get('logo')
        
        if nome:
            time = Time.objects.create(
                nome=nome,
                logo=logo
            )
            messages.success(request, f'Time "{nome}" cadastrado com sucesso!')
            return redirect('painel:lista_times')
        else:
            messages.error(request, 'O nome do time é obrigatório.')
    
    return render(request, 'painel/cadastrar_time.html')


@staff_member_required
def editar_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        logo = request.FILES.get('logo')
        
        if nome:
            time.nome = nome
            if logo:
                time.logo = logo
            time.save()
            messages.success(request, f'Time "{nome}" atualizado com sucesso!')
            return redirect('painel:lista_times')
        else:
            messages.error(request, 'O nome do time é obrigatório.')
    
    context = {
        'time': time,
    }
    return render(request, 'painel/editar_time.html', context)


@staff_member_required
def excluir_time(request, time_id):
    time = get_object_or_404(Time, id=time_id)
    
    if request.method == 'POST':
        nome = time.nome
        time.delete()
        messages.success(request, f'Time "{nome}" excluído com sucesso!')
        return redirect('painel:lista_times')
    
    context = {
        'time': time,
    }
    return render(request, 'painel/excluir_time.html', context)


@staff_member_required
def lista_jogadores(request):
    times = Time.objects.all().order_by('nome')
    posicoes = Jogador.POSICOES
    
    time_id = request.GET.get('time')
    posicao = request.GET.get('posicao')
    status = request.GET.get('status')
    busca = request.GET.get('busca', '')
    
    jogadores = Jogador.objects.select_related('time').all()
    
    if time_id and time_id != 'todos':
        jogadores = jogadores.filter(time_id=time_id)
    
    if posicao and posicao != 'todos':
        jogadores = jogadores.filter(posicao=posicao)
    
    if status and status != 'todos':
        if status == 'ativo':
            jogadores = jogadores.filter(ativo=True)
        elif status == 'inativo':
            jogadores = jogadores.filter(ativo=False)
    
    if busca:
        jogadores = jogadores.filter(
            Q(nome__icontains=busca) | 
            Q(time__nome__icontains=busca)
        )
    
    jogadores = jogadores.order_by('time', 'posicao', 'numero')
    total_resultados = jogadores.count()
    
    context = {
        'jogadores': jogadores,
        'times': times,
        'posicoes': posicoes,
        'filtros': {
            'time_id': time_id,
            'posicao': posicao,
            'status': status,
            'busca': busca,
        },
        'total_resultados': total_resultados,
    }
    return render(request, 'painel/jogadores.html', context)


@staff_member_required
def cadastrar_jogador(request):
    times = Time.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        time_id = request.POST.get('time')
        numero = request.POST.get('numero')
        posicao = request.POST.get('posicao')
        foto = request.FILES.get('foto')
        data_nascimento = request.POST.get('data_nascimento')
        nacionalidade = request.POST.get('nacionalidade')
        ativo = request.POST.get('ativo') == 'on'
        
        if nome and time_id:
            time = Time.objects.get(id=time_id)
            jogador = Jogador.objects.create(
                nome=nome,
                time=time,
                numero=numero if numero else None,
                posicao=posicao,
                foto=foto,
                data_nascimento=data_nascimento if data_nascimento else None,
                nacionalidade=nacionalidade if nacionalidade else 'Brasileiro',
                ativo=ativo
            )
            messages.success(request, f'Jogador "{nome}" cadastrado com sucesso!')
            return redirect('painel:lista_jogadores')
        else:
            messages.error(request, 'Nome e time são obrigatórios.')
    
    time_selecionado = request.GET.get('time')
    
    context = {
        'times': times,
        'posicoes': Jogador.POSICOES,
        'time_selecionado': time_selecionado,
    }
    return render(request, 'painel/cadastrar_jogador.html', context)


@staff_member_required
def editar_jogador(request, jogador_id):
    jogador = get_object_or_404(Jogador, id=jogador_id)
    times = Time.objects.all()
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        time_id = request.POST.get('time')
        numero = request.POST.get('numero')
        posicao = request.POST.get('posicao')
        foto = request.FILES.get('foto')
        data_nascimento = request.POST.get('data_nascimento')
        nacionalidade = request.POST.get('nacionalidade')
        ativo = request.POST.get('ativo') == 'on'
        
        if nome and time_id:
            jogador.nome = nome
            jogador.time_id = time_id
            jogador.numero = numero if numero else None
            jogador.posicao = posicao
            jogador.data_nascimento = data_nascimento if data_nascimento else None
            jogador.nacionalidade = nacionalidade if nacionalidade else 'Brasileiro'
            jogador.ativo = ativo
            
            if foto:
                jogador.foto = foto
                
            jogador.save()
            messages.success(request, f'Jogador "{nome}" atualizado com sucesso!')
            return redirect('painel:lista_jogadores')
        else:
            messages.error(request, 'Nome e time são obrigatórios.')
    
    context = {
        'jogador': jogador,
        'times': times,
        'posicoes': Jogador.POSICOES,
    }
    return render(request, 'painel/editar_jogador.html', context)


@staff_member_required
def excluir_jogador(request, jogador_id):
    jogador = get_object_or_404(Jogador, id=jogador_id)
    
    if request.method == 'POST':
        nome = jogador.nome
        jogador.delete()
        messages.success(request, f'Jogador "{nome}" excluído com sucesso!')
        return redirect('painel:lista_jogadores')
    
    context = {
        'jogador': jogador,
    }
    return render(request, 'painel/excluir_jogador.html', context)


@staff_member_required
def lista_jogos(request):
    times = Time.objects.all().order_by('nome')
    
    # Obter parâmetros dos filtros
    time_id = request.GET.get('time')
    rodada = request.GET.get('rodada')
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Query base
    jogos = Jogo.objects.select_related('time_casa', 'time_visitante').all()
    
    # Aplicar filtros
    if time_id and time_id != 'todos':
        jogos = jogos.filter(
            Q(time_casa_id=time_id) | Q(time_visitante_id=time_id)
        )
    
    if rodada and rodada != 'todos':
        try:
            rodada_int = int(rodada)
            jogos = jogos.filter(rodada=rodada_int)
        except ValueError:
            pass
    
    if status and status != 'todos':
        if status == 'realizado':
            jogos = jogos.filter(realizado=True)
        elif status == 'agendado':
            jogos = jogos.filter(realizado=False, data_jogo__gte=timezone.now())
        elif status == 'atrasado':
            jogos = jogos.filter(realizado=False, data_jogo__lt=timezone.now())
    
    if data_inicio:
        jogos = jogos.filter(data_jogo__date__gte=data_inicio)
    
    if data_fim:
        jogos = jogos.filter(data_jogo__date__lte=data_fim)
    
    # Obter lista de rodadas únicas para o filtro
    rodadas_disponiveis = Jogo.objects.values_list('rodada', flat=True).distinct().order_by('rodada')
    
    # Ordenar
    jogos = jogos.order_by('-data_jogo')
    total_resultados = jogos.count()
    
    context = {
        'jogos': jogos,
        'times': times,
        'rodadas_disponiveis': rodadas_disponiveis,
        'filtros': {
            'time_id': time_id,
            'rodada': rodada,
            'status': status,
            'data_inicio': data_inicio,
            'data_fim': data_fim,
        },
        'total_resultados': total_resultados,
    }
    return render(request, 'painel/jogos.html', context)


@staff_member_required
def cadastrar_jogo(request):
    times = Time.objects.all()
    
    if request.method == 'POST':
        time_casa_id = request.POST.get('time_casa')
        time_visitante_id = request.POST.get('time_visitante')
        data_jogo = request.POST.get('data_jogo')
        local = request.POST.get('local')
        rodada = request.POST.get('rodada')
        realizado = request.POST.get('realizado') == 'on'
        
        if time_casa_id and time_visitante_id and data_jogo and time_casa_id != time_visitante_id:
            time_casa = Time.objects.get(id=time_casa_id)
            time_visitante = Time.objects.get(id=time_visitante_id)
            
            jogo = Jogo.objects.create(
                time_casa=time_casa,
                time_visitante=time_visitante,
                data_jogo=data_jogo,
                local=local,
                rodada=rodada if rodada else 1,
                realizado=realizado
            )
            messages.success(request, 'Jogo cadastrado com sucesso!')
            return redirect('painel:lista_jogos')
        else:
            messages.error(request, 'Preencha todos os campos e escolha times diferentes.')
    
    context = {
        'times': times,
    }
    return render(request, 'painel/cadastrar_jogo.html', context)


@staff_member_required
def editar_jogo(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)
    times = Time.objects.all()
    
    if request.method == 'POST':
        time_casa_id = request.POST.get('time_casa')
        time_visitante_id = request.POST.get('time_visitante')
        data_jogo = request.POST.get('data_jogo')
        local = request.POST.get('local')
        rodada = request.POST.get('rodada')
        realizado = request.POST.get('realizado') == 'on'
        gols_casa = request.POST.get('gols_casa', 0)
        gols_visitante = request.POST.get('gols_visitante', 0)
        
        if time_casa_id and time_visitante_id and data_jogo and time_casa_id != time_visitante_id:
            jogo.time_casa_id = time_casa_id
            jogo.time_visitante_id = time_visitante_id
            jogo.data_jogo = data_jogo
            jogo.local = local
            jogo.rodada = rodada if rodada else 1
            jogo.realizado = realizado
            jogo.gols_casa = int(gols_casa)
            jogo.gols_visitante = int(gols_visitante)
            jogo.save()
            
            messages.success(request, 'Jogo atualizado com sucesso!')
            return redirect('painel:lista_jogos')
        else:
            messages.error(request, 'Preencha todos os campos e escolha times diferentes.')
    
    context = {
        'jogo': jogo,
        'times': times,
    }
    return render(request, 'painel/editar_jogo.html', context)


@staff_member_required
def excluir_jogo(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)
    
    if request.method == 'POST':
        descricao = str(jogo)
        jogo.delete()
        messages.success(request, f'Jogo "{descricao}" excluído com sucesso!')
        return redirect('painel:lista_jogos')
    
    context = {
        'jogo': jogo,
    }
    return render(request, 'painel/excluir_jogo.html', context)


@staff_member_required
def lancar_resultado(request, jogo_id):
    jogo = get_object_or_404(Jogo, id=jogo_id)
    jogadores_casa = jogo.time_casa.jogadores.filter(ativo=True)
    jogadores_visitante = jogo.time_visitante.jogadores.filter(ativo=True)
    
    if request.method == 'POST':
        gols_casa = request.POST.get('gols_casa', 0)
        gols_visitante = request.POST.get('gols_visitante', 0)
        
        jogo.gols_casa = int(gols_casa)
        jogo.gols_visitante = int(gols_visitante)
        jogo.realizado = True
        jogo.save()
        
        messages.success(request, 'Resultado lançado com sucesso!')
        return redirect('painel:lista_jogos')
    
    context = {
        'jogo': jogo,
        'jogadores_casa': jogadores_casa,
        'jogadores_visitante': jogadores_visitante,
    }
    return render(request, 'painel/lancar_resultado.html', context)


# ========== NOVAS VIEWS PARA GOLS ==========

@staff_member_required
def lista_gols(request):
    times = Time.objects.all().order_by('nome')
    jogadores = Jogador.objects.all().order_by('nome')
    
    # Obter parâmetros dos filtros
    time_id = request.GET.get('time')
    jogador_id = request.GET.get('jogador')
    jogo_id = request.GET.get('jogo')
    
    # Query base
    gols = Gol.objects.select_related('jogo', 'jogador', 'time').all().order_by('-data_cadastro')
    
    # Aplicar filtros
    if time_id and time_id != 'todos':
        gols = gols.filter(time_id=time_id)
    
    if jogador_id and jogador_id != 'todos':
        gols = gols.filter(jogador_id=jogador_id)
    
    if jogo_id and jogo_id != 'todos':
        gols = gols.filter(jogo_id=jogo_id)
    
    total_resultados = gols.count()
    
    # Obter lista de jogos para o filtro
    jogos_disponiveis = Jogo.objects.filter(realizado=True).order_by('-data_jogo')
    
    context = {
        'gols': gols,
        'times': times,
        'jogadores': jogadores,
        'jogos_disponiveis': jogos_disponiveis,
        'filtros': {
            'time_id': time_id,
            'jogador_id': jogador_id,
            'jogo_id': jogo_id,
        },
        'total_resultados': total_resultados,
    }
    return render(request, 'painel/gols.html', context)


@staff_member_required
def cadastrar_gol(request):
    times = Time.objects.all().order_by('nome')
    jogos = Jogo.objects.filter(realizado=True).order_by('-data_jogo')
    jogadores = Jogador.objects.filter(ativo=True).order_by('nome')
    
    if request.method == 'POST':
        jogo_id = request.POST.get('jogo')
        jogador_id = request.POST.get('jogador')
        time_id = request.POST.get('time')
        minuto = request.POST.get('minuto')
        tipo = request.POST.get('tipo')
        contra = request.POST.get('contra') == 'on'
        
        if jogo_id and jogador_id and time_id and minuto:
            jogo = Jogo.objects.get(id=jogo_id)
            jogador = Jogador.objects.get(id=jogador_id)
            time = Time.objects.get(id=time_id)
            
            gol = Gol.objects.create(
                jogo=jogo,
                jogador=jogador,
                time=time,
                minuto=minuto,
                tipo=tipo,
                contra=contra
            )
            messages.success(request, f'Gol de {jogador.nome} cadastrado com sucesso!')
            return redirect('painel:lista_gols')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    # Pré-selecionar valores se passados na URL
    jogo_selecionado = request.GET.get('jogo')
    time_selecionado = request.GET.get('time')
    jogador_selecionado = request.GET.get('jogador')
    
    # Filtrar jogadores por time se time selecionado
    if time_selecionado:
        jogadores = jogadores.filter(time_id=time_selecionado)
    
    context = {
        'times': times,
        'jogos': jogos,
        'jogadores': jogadores,
        'tipos_gol': Gol.TIPOS_GOL,
        'jogo_selecionado': jogo_selecionado,
        'time_selecionado': time_selecionado,
        'jogador_selecionado': jogador_selecionado,
    }
    return render(request, 'painel/cadastrar_gol.html', context)


@staff_member_required
def editar_gol(request, gol_id):
    gol = get_object_or_404(Gol, id=gol_id)
    times = Time.objects.all().order_by('nome')
    jogos = Jogo.objects.filter(realizado=True).order_by('-data_jogo')
    jogadores = Jogador.objects.filter(ativo=True).order_by('nome')
    
    if request.method == 'POST':
        jogo_id = request.POST.get('jogo')
        jogador_id = request.POST.get('jogador')
        time_id = request.POST.get('time')
        minuto = request.POST.get('minuto')
        tipo = request.POST.get('tipo')
        contra = request.POST.get('contra') == 'on'
        
        if jogo_id and jogador_id and time_id and minuto:
            gol.jogo_id = jogo_id
            gol.jogador_id = jogador_id
            gol.time_id = time_id
            gol.minuto = minuto
            gol.tipo = tipo
            gol.contra = contra
            gol.save()
            
            messages.success(request, 'Gol atualizado com sucesso!')
            return redirect('painel:lista_gols')
        else:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
    
    context = {
        'gol': gol,
        'times': times,
        'jogos': jogos,
        'jogadores': jogadores,
        'tipos_gol': Gol.TIPOS_GOL,
    }
    return render(request, 'painel/editar_gol.html', context)


@staff_member_required
def excluir_gol(request, gol_id):
    gol = get_object_or_404(Gol, id=gol_id)
    
    if request.method == 'POST':
        descricao = str(gol)
        gol.delete()
        messages.success(request, f'Gol excluído com sucesso!')
        return redirect('painel:lista_gols')
    
    context = {
        'gol': gol,
    }
    return render(request, 'painel/excluir_gol.html', context)


@staff_member_required
def carregar_jogadores_por_time(request):
    time_id = request.GET.get('time_id')
    jogadores = Jogador.objects.filter(time_id=time_id, ativo=True).order_by('nome')
    return render(request, 'painel/jogadores_dropdown.html', {'jogadores': jogadores})