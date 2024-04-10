from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from contrib.data_migrate import (create_setores_postos_trabalho,
                                  create_unidades, create_users, migrate)
from render.models import (ListaAtividades,
                           ListaIndicadoresMetricasTeletrabalho,
                           ListaSistemasTeletrabalho, Unidade)


class Command(BaseCommand):
    help = "Make custom migrations to app models"

    def handle(self, *args, **kwargs):
        # grupos
        _GROUPS = ['SERVIDORES', 'CHEFIAS', 'GABINETE', 'CIGT']

        for group_name in _GROUPS:
            try:
                group = Group.objects.get(name=group_name)
                print(f'[ok] Grupo {group.name} já existe.')
            except Group.DoesNotExist:
                group = Group.objects.create(name=group_name)
                print(f'[+] Grupo {group.name} criado.')

        # unidades, setores, postos de trabalho
        create_unidades()
        create_setores_postos_trabalho()

        # lista de atividades
        migrate('contrib/data/lista_atividades.txt',
                model=ListaAtividades,
                field='atividade')

        # lista de indicadores e métricas
        migrate('contrib/data/lista_indicadores_metricas.txt',
                model=ListaIndicadoresMetricasTeletrabalho,
                field='indicador')

        # lista de sistemas
        migrate('contrib/data/lista_sistemas.txt',
                model=ListaSistemasTeletrabalho,
                field='sistema')

        # lista de usuarios
        create_users('contrib/data/lista_usuarios.txt')
