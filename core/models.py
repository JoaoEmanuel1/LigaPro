# core/models.py

from django.db import models

class Time(models.Model):
    nome = models.CharField('Nome do Time', max_length=100)
    logo = models.ImageField('Logo', upload_to='logos/', null=True, blank=True)
    data_criacao = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Time'
        verbose_name_plural = 'Times'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Jogador(models.Model):
    POSICOES = [
        ('GOL', 'Goleiro'),
        ('ZAG', 'Zagueiro'),
        ('LAT', 'Lateral'),
        ('VOL', 'Volante'),
        ('MEI', 'Meio-campo'),
        ('ATA', 'Atacante'),
        ('TEC', 'Técnico'),
    ]
    
    nome = models.CharField('Nome do Jogador', max_length=100)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='jogadores', verbose_name='Time')
    numero = models.IntegerField('Número da Camisa', null=True, blank=True)
    posicao = models.CharField('Posição', max_length=3, choices=POSICOES)
    foto = models.ImageField('Foto', upload_to='jogadores/', null=True, blank=True)
    data_nascimento = models.DateField('Data de Nascimento', null=True, blank=True)
    nacionalidade = models.CharField('Nacionalidade', max_length=50, default='Brasileiro')
    ativo = models.BooleanField('Ativo?', default=True)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Jogador'
        verbose_name_plural = 'Jogadores'
        ordering = ['time', 'posicao', 'numero']
    
    def __str__(self):
        return f'{self.nome} ({self.get_posicao_display()})'


class Jogo(models.Model):
    time_casa = models.ForeignKey(
        Time, 
        on_delete=models.CASCADE, 
        related_name='jogos_como_casa',
        verbose_name='Time da Casa'
    )
    time_visitante = models.ForeignKey(
        Time, 
        on_delete=models.CASCADE, 
        related_name='jogos_como_visitante',
        verbose_name='Time Visitante'
    )
    gols_casa = models.IntegerField('Gols do Time da Casa', default=0)
    gols_visitante = models.IntegerField('Gols do Time Visitante', default=0)
    data_jogo = models.DateTimeField('Data do Jogo')
    local = models.CharField('Local do Jogo', max_length=200, blank=True, null=True)
    rodada = models.IntegerField('Rodada', default=1)
    realizado = models.BooleanField('Jogo Realizado?', default=False)
    
    class Meta:
        verbose_name = 'Jogo'
        verbose_name_plural = 'Jogos'
        ordering = ['-data_jogo']
    
    def __str__(self):
        if self.realizado:
            return f'Rodada {self.rodada}: {self.time_casa} {self.gols_casa} x {self.gols_visitante} {self.time_visitante}'
        else:
            return f'Rodada {self.rodada}: {self.time_casa} x {self.time_visitante} - {self.data_jogo.strftime("%d/%m/%Y %H:%M") if self.data_jogo else "Data a definir"}'


class Gol(models.Model):
    TIPOS_GOL = [
        ('NORMAL', 'Normal'),
        ('PENALTI', 'Pênalti'),
        ('FALTA', 'Falta'),
        ('CONTRA', 'Contra'),
    ]
    
    jogo = models.ForeignKey(Jogo, on_delete=models.CASCADE, related_name='gols', verbose_name='Jogo')
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, related_name='gols', verbose_name='Jogador')
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='gols', verbose_name='Time')
    minuto = models.IntegerField('Minuto do Gol')
    tipo = models.CharField('Tipo de Gol', max_length=10, choices=TIPOS_GOL, default='NORMAL')
    contra = models.BooleanField('Gol Contra?', default=False)
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Gol'
        verbose_name_plural = 'Gols'
        ordering = ['jogo', 'minuto']
    
    def __str__(self):
        return f'{self.jogador.nome} ({self.minuto}\') - {self.jogo}'