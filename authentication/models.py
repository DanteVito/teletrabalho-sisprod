import string

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    """
    Define a model manager for User model with no username field
    """

    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Cria e salva um usuário, dado seu username e senha
        """
        if not username:
            raise ValueError('O nome do usuário é obrigatório!')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        """
        Cria e salva usuário comum da aplicação
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        """
        Cria e salva superusuário com todas as permissões de admin
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("Usuário", max_length=255, unique=True)
    nome = models.CharField("Nome", max_length=255)
    rg = models.CharField("RG", max_length=255)
    cargo = models.CharField("Cargo", max_length=255)
    ramal = models.IntegerField("Ramal", null=True, blank=True)
    celular = models.CharField(
        "Celular", max_length=255, null=True, blank=True)
    email = models.CharField("E-mail", max_length=255, null=True, blank=True)
    cidade = models.CharField("Cidade", max_length=255, null=True, blank=True)
    is_staff = models.BooleanField("Membro da equipe", default=False, help_text="Define se o usuário tem acesso ao admin")  # noqa E501
    is_active = models.BooleanField("Ativo", default=False, help_text="Define se o usuário ativou a conta no email")  # noqa E501
    date_joined = models.DateTimeField("Criação", auto_now_add=True)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.nome

    def get_group_set(self):
        """
        Método que retorna um set
        contendo os nomes dos grupos
        de um usuário
        """
        return {group.name for group in self.groups.all()}

    def check_dados(self):
        _DADOS = ('ramal', 'celular', 'email', 'cidade')
        missing_data = []
        for d in _DADOS:
            dado = getattr(self, d)
            if not dado:
                missing_data.append(d)
        return missing_data

    def get_dict(self):
        """
        Método que retorna um dicionário com chave/valor
        como field/value.
        """
        return {
            'username': self.username,
            'nome': self.nome,
            'rg': self.rg,
            'cargo': self.cargo,
            'ramal': self.ramal,
            'celular': self.celular,
            'email': self.email,
            'cidade': self.cidade,
            'is_staff': self.is_staff,
            'is_active': self.is_active,
            'date_joined': self.date_joined,
        }

    def rg_format(self) -> str:
        """
        Método que formata corretamente
        o RG com a máscara XX.XXX.XXX-X
        """
        # remove puntuação
        no_punctuation_field = self.rg.translate(
            str.maketrans('', '', string.punctuation))
        # converte para int e depois para str
        numeric = int(no_punctuation_field)
        clean_field = str(numeric)
        # convertemos em uma lista para inserir a pontuação
        lista_field = list(clean_field)
        lista_field.insert(-1, '-')
        lista_field.insert(-5, '.')
        if len(clean_field) > 7:
            lista_field.insert(-9, '.')

        return ''.join(lista_field)

    class Meta:
        ordering = ('nome', )
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
