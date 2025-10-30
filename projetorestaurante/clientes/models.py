from django.db import models

class Pessoa(models.Model):
    nome = models.CharField(max_length=50)
    telefone = models.IntegerField()
    email = models.CharField(max_length=100)
    quantidade = models.IntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome
   