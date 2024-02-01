from django.core.management.base import BaseCommand

from contrib.data_migrate import (create_users, migrate,
                                  migrate_setores_postos_de_trabalho)
from render.models import (ListaAtividades,
                           ListaIndicadoresMetricasTeletrabalho,
                           ListaSistemasTeletrabalho, Unidade)


class Command(BaseCommand):
    help = "Make custom migrations to app models"

    def handle(self, *args, **kwargs):

        # unidades
        migrate(
            'contrib/data/lista_unidades.txt',
            model=Unidade,
            field='nome')

        # setores e postos de trabalho
        migrate_setores_postos_de_trabalho(
            'contrib/data/postos_de_trabalho.txt')

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
