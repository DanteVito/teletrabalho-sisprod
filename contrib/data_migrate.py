import csv
import string

from django.db.utils import IntegrityError
from unidecode import unidecode

from authentication.models import User
from render.models import (Cargo, Lotacao, PostosTrabalho, Servidor, Setor,
                           Unidade)


def strip_remove_ponctuation(s: str) -> str:
    s = s.strip()
    s = s.upper()
    s = unidecode(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s


def create_unidades(file='contrib/data/postos_de_trabalho.txt') -> None:
    unidades_set = set()
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            data_line = line.split('\t')
            sigla = data_line[0].split('/')
            # orgao = sigla[0]
            unidade = sigla[1]
            # setor = sigla[2]
            unidades_set.add(unidade)

    unidades = list(unidades_set)
    unidades.sort()

    for unidade in unidades:
        data_unidade = {
            'nome': unidade,
            'sigla': unidade
        }
        Unidade.objects.update_or_create(**data_unidade)


def create_setores_postos_trabalho(file='contrib/data/postos_de_trabalho.txt') -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            data_line = line.split('\t')
            sigla = data_line[0].split('/')[1]
            unidade = Unidade.objects.get(sigla=sigla)
            setor = data_line[0].split('/')[2]
            data_setor = {
                'unidade': unidade,
                'nome': setor,
                'sigla': setor
            }
            setor, _ = Setor.objects.update_or_create(**data_setor)

            posto_trabalho = data_line[1]
            tipo_posto_trabalho = data_line[2]

            data_posto_trabalho = {
                'setor': setor,
                'posto': posto_trabalho,
                'tipo': tipo_posto_trabalho,
            }

            PostosTrabalho.objects.update_or_create(**data_posto_trabalho)


def create_users(file: str) -> None:
    try:
        admin = User.objects.create_superuser(
            username='admin',
            password='admin',
            nome='admin',
        )
        print(f'[+ criado superusuário]: {admin.username}')
    except IntegrityError:
        ...

    with open(file, 'r', encoding='utf-8') as f:
        for item in f:
            data_item = item.strip().split(',')
            username = data_item[0]
            data = {
                'username': username,
                'rg': data_item[1],
                'nome': strip_remove_ponctuation(data_item[2]),
                'password': 'repr2024',
                'is_active': True
            }
            try:
                user = User.objects.create_user(**data)
                print(f'[+] {user.username} - {user.nome} -> adicionado')
            except IntegrityError:
                user = User.objects.get(username=username)
                print(
                    f'[!] {user.username} - {user.nome} -> já existente')

            # cria cargo
            nome_cargo = strip_remove_ponctuation(data_item[3])
            cargo, cargo_created = Cargo.objects.update_or_create(
                nome=nome_cargo,
            )
            if cargo_created:
                print(f'[+ cargo] {cargo}')
            # cria servidor
            servidor, servidor_created = Servidor.objects.update_or_create(
                user=user,
                cargo=cargo
            )
            if servidor_created:
                print(f'[+ servidor] {servidor.user.nome}')

            # cria lotacao
            lotacao, lotacao_created = Lotacao.objects.update_or_create(
                servidor=servidor
            )
            if lotacao_created:
                print(f'[+ lotação] {lotacao}')


def migrate(file: str, model, field: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for value in f:
            data = {field: value.strip()}
            obj, _ = model.objects.update_or_create(**data)
            print(obj)


# def migrate_setores_postos_de_trabalho(file: str) -> None:
#     with open(file, 'r', encoding='utf-8') as f:
#         sectors = set()
#         for line in f:
#             values = line.strip().split('\t')
#             data_posto = {
#                 'setor': values[0].strip().replace('/', '-'),
#                 'posto': values[1].strip(),
#                 'tipo': values[2].strip(),
#             }
#             posto_de_trabalho, _ = PostosTrabalho.objects.update_or_create(  # noqa E501
#                 **data_posto)
#             print(posto_de_trabalho)
#             sectors.add(values[0].replace('/', '-'))

#     for sector in sectors:
#         data_setor = {'nome': sector}
#         Setor.objects.update_or_create(**data_setor)
