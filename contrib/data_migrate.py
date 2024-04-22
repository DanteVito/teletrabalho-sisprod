import csv
import string

from decouple import config
from django.db.utils import IntegrityError
from unidecode import unidecode

from authentication.models import User
from render.models import (Cargo, Chefia, Lotacao, PostosTrabalho, Servidor,
                           Setor, Unidade)


def strip_remove_ponctuation(s: str) -> str:
    s = s.strip()
    s = s.upper()
    s = unidecode(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s


def create_unidades(file: str) -> None:
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


def create_setores_postos_trabalho(file: str) -> None:
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

            posto_trabalho = data_line[1].strip()
            tipo_posto_trabalho = data_line[2].strip()
            chefia = data_line[3].strip()

            if chefia == 'CHEFIA':
                chefia = True
            else:
                chefia = False

            data_posto_trabalho = {
                'setor': setor,
                'posto': posto_trabalho,
                'tipo': tipo_posto_trabalho,
                'chefia': chefia,
            }

            posto_trabalho, posto_trabalho_created = PostosTrabalho.objects.update_or_create(
                **data_posto_trabalho)

            if posto_trabalho_created:
                print(f'[criado posto de trabalho] {posto_trabalho}')


def create_users(file: str) -> None:
    try:
        admin = User.objects.create_superuser(
            username='admin',
            password=config('ADMIN'),
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
            # adiciona posto de trabalho na lotacao do servidor
            try:
                # posição 4 - unidade
                # posição 5 - setor
                # posição 6 - posto de trabalho
                unidade_sigla = data_item[4]
                setor_sigla = data_item[5]
                posto_trabalho_posto = data_item[6]
                unidade = Unidade.objects.get(sigla=unidade_sigla)
                setor = Setor.objects.get(
                    unidade=unidade, sigla=setor_sigla)
                posto_trabalho = PostosTrabalho.objects.get(
                    setor=setor,
                    posto=posto_trabalho_posto
                )

                lotacao, created = Lotacao.objects.update_or_create(
                    servidor=servidor,
                    posto_trabalho=posto_trabalho
                )

                if not created:
                    print(
                        f'[+ posto de trabalho {posto_trabalho} -> {servidor}]')

            except IndexError:
                lotacao, lotacao_created = Lotacao.objects.update_or_create(
                    servidor=servidor
                )
                if lotacao_created:
                    print(f'[+ lotação] {lotacao}')


def create_chefias(file: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for item in f:
            data_item = item.strip().split(',')
            # servidor
            # posicao 0: unidade posto_trabalho
            sigla_posto_trabalho = data_item[0]
            unidade_servidor = Unidade.objects.get(sigla=sigla_posto_trabalho)
            # posicao 1: setor posto_trabalho
            sigla_setor_posto_trabalho = data_item[1]
            setor_servidor = Setor.objects.get(
                unidade=unidade_servidor,
                sigla=sigla_setor_posto_trabalho
            )
            # posicao 2: posto posto_trabalho
            posto_posto_trabalho = data_item[2]
            posto_trabalho_servidor = PostosTrabalho.objects.get(
                setor=setor_servidor,
                posto=posto_posto_trabalho
            )
            # chefia
            # posicao 3: unidade posto_trabalho chefia
            sigla_posto_trabalho_chefia = data_item[3]
            unidade_chefia = Unidade.objects.get(
                sigla=sigla_posto_trabalho_chefia)
            # posicao 4: setor posto_trabalho chefia
            sigla_setor_posto_trabalho_chefia = data_item[4]
            setor_chefia = Setor.objects.get(
                unidade=unidade_chefia,
                sigla=sigla_setor_posto_trabalho_chefia
            )
            # posicao 5: unidade posto_trabalho chefia
            posto_posto_trabalho_chefia = data_item[5]
            posto_trabalho_chefia = PostosTrabalho.objects.get(
                setor=setor_chefia,
                posto=posto_posto_trabalho_chefia
            )

            _, created = Chefia.objects.update_or_create(
                posto_trabalho=posto_trabalho_servidor,
                posto_trabalho_chefia=posto_trabalho_chefia
            )

            if created:
                print(
                    f'[+ relacionamento chefia adicionado] {posto_trabalho_servidor} -> {posto_trabalho_chefia}')


def migrate(file: str, model, field: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for value in f:
            data = {field: value.strip()}
            obj, _ = model.objects.update_or_create(**data)
            print(obj)
