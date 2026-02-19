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
    rodada = models.IntegerField('Rodada', default=1)  # <-- NOVO CAMPO
    realizado = models.BooleanField('Jogo Realizado?', default=False)
    
    class Meta:
        verbose_name = 'Jogo'
        verbose_name_plural = 'Jogos'
        ordering = ['rodada', 'data_jogo']  # Ordena por rodada primeiro
    
    def __str__(self):
        if self.realizado:
            return f'Rodada {self.rodada}: {self.time_casa} {self.gols_casa} x {self.gols_visitante} {self.time_visitante}'
        else:
            return f'Rodada {self.rodada}: {self.time_casa} x {self.time_visitante} - {self.data_jogo.strftime("%d/%m/%Y %H:%M") if self.data_jogo else "Data a definir"}'