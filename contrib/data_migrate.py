import string

from django.db.utils import IntegrityError
from unidecode import unidecode

from authentication.models import User
from render.models import ListaPostosTrabalho, Setor


def strip_remove_ponctuation(s: str) -> str:
    s = s.strip()
    s = s.upper()
    s = unidecode(s)
    s = s.translate(str.maketrans('', '', string.punctuation))
    return s


def create_users(file: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for item in f:
            data_item = item.strip().split(',')
            username = data_item[0]
            data = {
                'username': username,
                'rg': data_item[1],
                'nome': strip_remove_ponctuation(data_item[2]),
                'cargo': strip_remove_ponctuation(data_item[3]),
                'password': 'repr2024',
                'is_active': True
            }
            try:
                User.objects.create_user(**data)
                print(f'[+] {data["username"]} - {data["nome"]} -> adicionado')
            except IntegrityError:
                print(
                    f'[!] {data["username"]} - {data["nome"]} -> já existente')


def migrate(file: str, model, field: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        for value in f:
            data = {field: value.strip()}
            obj, _ = model.objects.update_or_create(**data)
            print(obj)


def migrate_setores_postos_de_trabalho(file: str) -> None:
    with open(file, 'r', encoding='utf-8') as f:
        sectors = set()
        for line in f:
            values = line.strip().split('\t')
            data_posto = {
                'setor': values[0].strip().replace('/', '-'),
                'posto': values[1].strip(),
                'tipo': values[2].strip(),
            }
            posto_de_trabalho, _ = ListaPostosTrabalho.objects.update_or_create(  # noqa E501
                **data_posto)
            print(posto_de_trabalho)
            sectors.add(values[0].replace('/', '-'))

    for sector in sectors:
        data_setor = {'nome': sector}
        Setor.objects.update_or_create(**data_setor)
