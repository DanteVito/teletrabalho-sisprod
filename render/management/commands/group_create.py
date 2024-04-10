from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create User Groups to the application"

    def handle(self, *args, **kwargs):

        _GROUPS = ['SERVIDORES', 'CHEFIAS', 'GABINETE', 'CIGT']

        for group_name in _GROUPS:
            try:
                group = Group.objects.get(name=group_name)
                print(f'[ok] Grupo {group.name} já existe.')
            except Group.DoesNotExist:
                print(f'[+] Criando grupo {group.name} ...')
                Group.objects.create(name=group_name)
