import calendar
import os
import string
import typing
from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files import File
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ProtectedError, Q
from django.db.models.signals import (post_delete, post_save, pre_delete,
                                      pre_save)
from django.dispatch import receiver
from django.http import HttpResponse
from django.utils import timezone
from docxtpl import DocxTemplate
from prettytable import PrettyTable

from authentication.models import User


class ComissaoInterna(models.Model):
    _FUNCAO = {
        ('presidente', 'Presidente'),
        ('membro', 'Membro'),
    }
    user = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_cigt', on_delete=models.CASCADE, null=True)  # noqa E501
    nome = models.CharField(max_length=255)
    funcao = models.CharField(max_length=128, choices=_FUNCAO,)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Comissão Interna'
        verbose_name_plural = 'Admin | Comissão Interna'


class Unidade(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = 'Unidade'
        verbose_name_plural = 'Admin | Unidades'


class Setor(models.Model):
    nome = models.CharField(max_length=255)

    def __str__(self):
        return self.nome

    class Meta:
        ordering = ['nome']
        verbose_name = 'Setor'
        verbose_name_plural = 'Admin | Setores'


class ListaPostosTrabalho(models.Model):
    setor = models.CharField(max_length=255, null=True, blank=True)
    posto = models.CharField(max_length=255)
    tipo = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.setor}: {self.posto}'

    class Meta:
        verbose_name = 'Lista de Postos de Trabalho'
        verbose_name_plural = 'Admin | Lista de Postos de Trabalho'


class ModeloDocumento(models.Model):
    """
    Classe para a inclusão modelos de documentos (templates).
    """
    setor = models.ForeignKey(Setor,
                              related_name='%(app_label)s_%(class)s_setor',
                              on_delete=models.CASCADE)
    nome_modelo = models.CharField(max_length=128)
    descricao_modelo = models.TextField()
    template_docx = models.FileField(upload_to='templates_docx/')

    def __str__(self):
        return self.nome_modelo

    class Meta:
        verbose_name = 'Modelo docx'
        verbose_name_plural = 'Admin | Modelos docx'


class BaseModelMethods(models.Model):
    """
    Base model contendo os métodos 
    utilizados para geração dos documentos
    """
    data = models.DateField(default=timezone.now)  # noqa E501
    data_edicao = models.DateTimeField(auto_now=True)  # noqa E501
    data_criacao = models.DateTimeField(auto_now_add=True)  # noqa E501
    modelo = models.ForeignKey(ModeloDocumento, related_name="%(app_label)s_%(class)s_modelo", on_delete=models.CASCADE)  # noqa E501
    docx = models.FileField(upload_to='generated_docx/', blank=True, null=True)  # noqa E501
    pdf = models.FileField(upload_to='generated_pdf/', blank=True, null=True)  # noqa E501

    def get_verbose_month(cls, month: int) -> str:
        verbose_months = {
            1: 'Janeiro',
            2: 'Fevereiro',
            4: 'Março',
            3: 'Abril',
            5: 'Maio',
            6: 'Junho',
            7: 'Julho',
            8: 'Agosto',
            9: 'Setembro',
            10: 'Outubro',
            11: 'Novembro',
            12: 'Dezembro',
        }
        return verbose_months[month]

    def get_date(self):
        return f'{self.data_edicao.day} de {self.get_verbose_month(self.data_edicao.month)} de {self.data_edicao.year}'  # noqa E501

    def get_context_docx(self):
        context = {
            'data': self.get_date()
        }
        return context

    def gerar_nome_arquivo(self, tipo_doc='manifestacao_interesse', file_type: str = "docx") -> str:  # noqa E501
        """
        Método para gerar nome do arquivo .docx ou .pdf
        """
        if file_type not in ('docx', 'pdf'):
            raise Exception('file_type accepts only "docx" and "pdf"')

        if hasattr(self, 'servidor'):
            nome_resumido = str(self.servidor)
        elif hasattr(self, 'despacho_cigt'):
            nome_resumido = str(
                self.despacho_cigt.plano_trabalho.manifestacao.servidor)
        else:
            nome_resumido = 'CIGT'

        if hasattr(self, 'numeracao'):
            base_name = f'{tipo_doc} {self.numeracao} {nome_resumido}'  # noqa E501
        else:
            base_name = f'{tipo_doc} {nome_resumido}'  # noqa E501
        base_name = base_name.replace(' ', '_')

        if tipo_doc == 'portaria_teletrabalho_doe':
            base_name = f'{tipo_doc}_{date.today()}_id_{self.id}'

        if file_type == 'docx':
            return base_name + '.docx'
        else:
            return base_name + '.pdf'

    def get_path_docx_template(self) -> str:
        """
        Este método retorna o path do arquivo de template docx
        associado a instância para ser renderizado pelo docxtpl
        com o método self.render_docx_tpl()
        """
        template_docx_name = os.path.basename(self.modelo.template_docx.name)
        path_template_docx = os.path.join(
            settings.TEMPLATE_DOCX_ROOT,
            template_docx_name
        )
        return path_template_docx

    def get_path_file_temp(self, tipo_doc: str, file_type: str = 'docx') -> str:  # noqa E501
        """
        Este método retorna o path temporário para geração de arquivos
        que posteriormente serão enviados para a pasta associada ao
        fileinput do campo do arquivo.
        """
        generated_name = self.gerar_nome_arquivo(tipo_doc=tipo_doc,
                                                 file_type=file_type)
        path_file_temp = os.path.join(
            settings.TEMP_FOLDER_ROOT, generated_name
        )
        return path_file_temp

    def render_docx_tpl(self, tipo_doc: str, save_input: bool = True) -> None:
        """
        Este método faz a renderização do contexto (dicionário)
        em um template .docx para a geração do documento final .docx.
        Utilizamos o pacote python-docx-template (docxtpl).
        """
        context_docx = self.get_context_docx()
        path_template_docx = self.get_path_docx_template()

        docx = DocxTemplate(path_template_docx)
        docx.render(context_docx)
        path_file_docx_temp = self.get_path_file_temp(tipo_doc=tipo_doc,  # noqa E501
                                                      file_type='docx')
        docx.save(path_file_docx_temp)
        if save_input and docx.is_saved:
            self.save_file_input(tipo_doc=tipo_doc, file_type='docx')

    def save_file_input(self, tipo_doc: str, file_type: str) -> None:
        """
        Método para fazer o input dos arquivos docx ou pdfs gerados no
        filefield do modelo.
        salva os arquivos docx em media/generated_docx
        salva os arquivo pdf em media/generated_pdf
        """
        if file_type not in ('docx', 'pdf'):
            raise Exception('file_type accepts only "docx" and "pdf"')

        if file_type == 'docx':
            path_root = settings.GENERATED_DOCX_ROOT
            # verifica se existe um arquivo docx gerado na pasta temp/
            path_file_temp = self.get_path_file_temp(tipo_doc=tipo_doc,
                                                     file_type=file_type)
            if os.path.exists(path_file_temp):
                filename = os.path.basename(path_file_temp)
                # verifica se já existe um arquivo com o mesmo nome na pasta
                # de destino. Se existir, deleta o arquivo para gerar um novo
                #  com o mesmo nome dentro desta pasta
                # if os.path.exists(os.path.join(path_root, filename)):
                #    os.remove(os.path.join(path_root, filename))

                # salva o arquivo no FileField
                # path_file_save

                with open(path_file_temp, 'rb') as f:
                    if file_type == 'docx':
                        self.docx = File(f, name=filename)
                    elif file_type == 'pdf':
                        self.pdf = File(f, name=filename)
                    self.save()

                # deleta o arquivo temporário gerado pelo docxtpl
                os.remove(path_file_temp)
            else:
                print(f'ErroArquivo: arquivo inexistente em {path_file_temp}')

        else:
            path_root = settings.GENERATED_PDF_ROOT
            # verifica se existe um arquivo pdf gerado na pasta temp/
            path_file_temp = self.get_path_file_temp(tipo_doc=tipo_doc,
                                                     file_type=file_type)
            if os.path.exists(path_file_temp):
                filename = os.path.basename(path_file_temp)
                if os.path.exists(os.path.join(path_root, filename)):
                    os.remove(os.path.join(path_root, filename))

                # salva o arquivo no FileField
                # path_file_save

                with open(path_file_temp, 'rb') as f:
                    if file_type == 'docx':
                        self.docx = File(f, name=filename)
                    elif file_type == 'pdf':
                        self.pdf = File(f, name=filename)
                    self.save()

                # deleta o arquivo temporário
                os.remove(path_file_temp)

    class Meta:
        verbose_name = 'Base Model Methods'
        verbose_name_plural = 'Base Model Methods'
        abstract = True


class BaseModelGeneral(BaseModelMethods):
    """
    Base model
    """
    adicionado_por = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_add_by', on_delete=models.CASCADE)  # noqa E501
    modificado_por = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_change_by', on_delete=models.CASCADE)  # noqa E501

    class Meta:
        verbose_name = 'Base Model General'
        verbose_name_plural = 'Base Model General'
        abstract = True


class BaseModelTeletrabalho(BaseModelGeneral):
    """
    Base model para os modelos do Teletrabalho
    """
    unidade = models.ForeignKey(Unidade, related_name="%(app_label)s_%(class)s_unidade", on_delete=models.CASCADE, null=True)  # noqa E501
    setor = models.ForeignKey(Setor, related_name='%(app_label)s_%(class)s_setor', null=True, on_delete=models.CASCADE)  # noqa E501

    class Meta:
        verbose_name = 'Base Model Teletrabalho'
        verbose_name_plural = 'Base Model Teletrabalho'
        abstract = True


class ListaIndicadoresMetricasTeletrabalho(models.Model):
    indicador = models.CharField(max_length=255)

    def __str__(self):
        return self.indicador

    class Meta:
        verbose_name = 'Lista de Indicadores'
        verbose_name_plural = 'Admin | Lista de Indicadores'


class ListaAtividades(models.Model):
    atividade = models.CharField(max_length=255)

    def __str__(self):
        return self.atividade

    class Meta:
        ordering = ('atividade', )
        verbose_name = 'Lista de Atividades'
        verbose_name_plural = 'Admin | Lista de Atividades'


class ListaSistemasTeletrabalho(models.Model):
    sistema = models.CharField(max_length=255)

    def __str__(self):
        return self.sistema

    class Meta:
        ordering = ('sistema', )
        verbose_name = 'Lista de Sistemas'
        verbose_name_plural = 'Admin | Lista de Sistemas'


class ManifestacaoInteresse(BaseModelGeneral):
    """
    Classe para registro das manifestações de interesse
    dos servidores
    """
    _APROVACAO = (
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    )
    unidade = models.ForeignKey(Unidade, related_name='%(app_label)s_%(class)s_unidade', on_delete=models.CASCADE, null=True)  # noqa E501
    setor = models.ForeignKey(Setor, related_name='%(app_label)s_%(class)s_setor', on_delete=models.CASCADE)  # noqa E501
    servidor = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_servidor', on_delete=models.CASCADE)  # noqa E501
    funcao = models.CharField("Função", max_length=255)
    posto_trabalho = models.ForeignKey(ListaPostosTrabalho, related_name='%(app_label)s_%(class)s_posto_trabalho_servidor', on_delete=models.CASCADE)  # noqa E501
    chefia_imediata = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_chefia_imediata', on_delete=models.CASCADE)  # noqa E501
    funcao_chefia = models.CharField("Função Chefia Imediata", max_length=255)
    posto_trabalho_chefia = models.ForeignKey(ListaPostosTrabalho, related_name='%(app_label)s_%(class)s_posto_trabalho_chefia', on_delete=models.CASCADE)  # noqa E501
    aprovado_chefia = models.CharField(
        choices=_APROVACAO, max_length=16, null=True, blank=True)

    def __str__(self) -> str:
        return f'Manifestação de Interesse: {self.servidor} | {self.data_criacao.strftime("%d/%m/%Y")}'

    @classmethod
    def get_manifestacoes_subordinados(cls, chefia_imediata):
        """
        Método que retorna todas as manifestações de interesse
        para uma chefia imediata
        """
        return cls.objects.filter(chefia_imediata=chefia_imediata)

    def clean(self):
        # bloqueia a edicao depois que a manifestacao for aprovada ou reprovada
        try:
            manifestacao_old = ManifestacaoInteresse.objects.get(id=self.id)
            if manifestacao_old.aprovado_chefia:
                raise ValidationError(
                    "Não é possível editar uma Manifestação de Interesse já aprovada/reprovada pela Chefia Imediata!")
        except ObjectDoesNotExist:
            ...

        # servidor
        if not self.servidor.ramal:
            raise ValidationError(
                "Preecha o campo 'Ramal' no cadastro do usuário (servidor)")
        if not self.servidor.celular:
            raise ValidationError(
                "Preecha o campo 'Celular' no cadastro do usuário (servidor)")
        if not self.servidor.email:
            raise ValidationError(
                "Preecha o campo 'E-mail' no cadastro do usuário (servidor)")
        if not self.servidor.cidade:
            raise ValidationError(
                "Preecha o campo 'Cidade' no cadastro do usuário (servidor)")
        # chefia
        if not self.chefia_imediata.ramal:
            raise ValidationError(
                "Preecha o campo 'Ramal' no cadastro do usuário (chefia imediata)")
        if not self.chefia_imediata.celular:
            raise ValidationError(
                "Preecha o campo 'Celular' no cadastro do usuário (chefia imediata)")
        if not self.chefia_imediata.email:
            raise ValidationError(
                "Preecha o campo 'E-mail' no cadastro do usuário (chefia imediata)")
        if not self.chefia_imediata.cidade:
            raise ValidationError(
                "Preecha o campo 'Cidade' no cadastro do usuário (chefia imediata)")

    def get_context_docx(self):
        context = {
            'unidade': self.unidade,
            'setor': self.setor,
            'servidor': self.servidor,
            'funcao': self.funcao,
            'data': self.get_date(),
            'posto_trabalho': self.posto_trabalho,
        }
        return context

    class Meta:
        verbose_name = 'Manifestação de Interesse'
        verbose_name_plural = 'Servidor | Manifestações de Interesse'


class DeclaracaoNaoEnquadramentoVedacoes(BaseModelGeneral):
    manifestacao = models.ForeignKey(ManifestacaoInteresse, related_name="%(app_label)s_%(class)s_interesse", on_delete=models.CASCADE)  # noqa E501
    estagio_probatorio = models.BooleanField('Não estou em estágio probatório')
    cargo_chefia_direcao = models.BooleanField('Não ocupo cargo de chefia ou direção')  # noqa E501
    penalidade_disciplinar = models.BooleanField('Não sofri penalidade disciplinar nos últimos 12 meses')  # noqa E501
    justificativa_excecao = models.TextField(
        "Justificativa Exceções", blank=True, null=True)

    def clean(self):
        if not self.estagio_probatorio or not self.penalidade_disciplinar:
            raise ValidationError(
                "É vedado o teletrabalho ao Servidor que se enquadra nas vedações legais")

        try:
            AutorizacoesExcecoes.objects.get(
                declaracao__manifestacao=self.manifestacao)
            raise ValidationError(
                "Não é possível alterar a Declaração de Não Enquadramento\
                    enquanto houver um Pedido de Autorização da Direção pendente\
                    para ocupante de cargo de chefia ou direção!\
                        Não é possível cadastrar nova Declaração se houver pendência\
                            de aprovação do Gabinete para a declaração selecionada!")
        except ObjectDoesNotExist:
            ...

    def get_context_docx(self):
        context = {
            'data': self.get_date(),
            'servidor': self.manifestacao.servidor,
            'estagio_probatorio': self.estagio_probatorio,
            'cargo_chefia_direcao': self.cargo_chefia_direcao,
            'penalidade_disciplinar': self.penalidade_disciplinar,
        }
        return context

    def __str__(self):
        return f'Declaração Não Enquadramento Vedações: {self.manifestacao.servidor}'

    class Meta:
        verbose_name = 'Declaração Não Enquadramento Vedações'
        verbose_name_plural = 'Servidor | Declarações Não Enquadramento Vedações'


class AutorizacoesExcecoes(BaseModelMethods):
    #
    # reescrever um modelo base para usar aqui com as funcoes basicas: data e geracao de docx, pdf, etc,
    # criar um modelo mais simples que o BaseModelGeneral
    #
    _APROVACAO = (
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    )
    data_criacao = models.DateTimeField(auto_now_add=True)  # noqa E501
    data_edicao = models.DateTimeField(auto_now=True)  # noqa E501
    declaracao = models.ForeignKey(DeclaracaoNaoEnquadramentoVedacoes, related_name="%(app_label)s_%(class)s_declaracao", on_delete=models.CASCADE)  # noqa E501
    modelo = models.ForeignKey(ModeloDocumento, related_name="%(app_label)s_%(class)s_modelo", on_delete=models.CASCADE)  # noqa E501
    aprovado_gabinete = models.CharField(
        choices=_APROVACAO, max_length=16, null=True, blank=True)
    modificado_por = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user_aprovacao', on_delete=models.CASCADE, null=True)  # noqa E501

    def __str__(self):
        return f'Autorização Teletrabalho Chefia: {self.declaracao}'

    def clean(self):
        try:
            old_autorizacao = AutorizacoesExcecoes.objects.get(id=self.id)
            if old_autorizacao.aprovado_gabinete:
                raise ValidationError(
                    "Não é possível alterar uma autorização concedida/negada.")
        except AutorizacoesExcecoes.DoesNotExist:
            ...

    def get_context_docx(self):
        context = {
            'data': self.get_date(),
            'declaracao': self.declaracao,
            'modificado_por': self.modificado_por,
        }
        return context

    class Meta:
        verbose_name = 'Autorização Exceção Teletrabalho Chefia'
        verbose_name_plural = 'Direção | Autorizações Exceções Teletrabalho Chefias'


class PlanoTrabalho(BaseModelGeneral):
    _APROVACAO = (
        ('aprovado', 'Aprovado'),
        ('reprovado', 'Reprovado'),
    )
    manifestacao = models.ForeignKey(ManifestacaoInteresse, related_name="%(app_label)s_%(class)s_interesse", on_delete=models.CASCADE)  # noqa E501
    periodo_comparecimento = models.CharField(max_length=255, null=True)
    periodo_acionamento = models.CharField(max_length=255, null=True)
    sistemas = models.ManyToManyField(ListaSistemasTeletrabalho)
    aprovado_chefia = models.CharField(
        choices=_APROVACAO, max_length=16, null=True, blank=True)
    aprovado_cigt = models.CharField(
        choices=_APROVACAO, max_length=16, null=True, blank=True)
    usuario_chefia_aprovacao = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user_chefia_aprovacao', on_delete=models.CASCADE, null=True)  # noqa E501
    usuario_cigt_aprovacao = models.ForeignKey(User, related_name='%(app_label)s_%(class)s_user_cigt_aprovacao', on_delete=models.CASCADE, null=True)  # noqa E501

    def clean(self):
        try:
            if not self.manifestacao.aprovado_chefia:
                raise ValidationError(
                    "É preciso ter a manifestação de interesse aprovada antes de elaborar o Plano de Trabalho!")
        except ObjectDoesNotExist:
            pass

        try:
            declaracao = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
                manifestacao__servidor=self.manifestacao.servidor).last()
            if not declaracao.estagio_probatorio or not declaracao.penalidade_disciplinar:
                raise ValidationError(
                    "Não é possível elaborar Plano de Trabalho para Servidor que se enquadra nas vedações legais")
            if not declaracao.cargo_chefia_direcao:
                try:
                    autorizacao = AutorizacoesExcecoes.objects.get(
                        declaracao=declaracao)
                    if autorizacao.aprovado_gabinete != 'aprovado':
                        raise ValidationError(
                            "É preciso autorização do Diretor do Órgão para teletrabalho de servidor com cargo de chefia")
                except ObjectDoesNotExist:
                    modelo = ModeloDocumento.objects.get(nome_modelo="APROVACAO EXCECAO DIRETOR")  # noqa E501
                    AutorizacoesExcecoes.objects.create(
                        declaracao=declaracao, modelo=modelo)
                    raise ValidationError(
                        "É preciso autorização do Diretor do Órgão para teletrabalho de servidor com cargo de chefia")
        except ObjectDoesNotExist:
            raise ValidationError(
                "É preciso preecher a Declaração de Não Enquadramento nas Vedações antes de elaborar o Plano de Trabalho!")

        try:
            plano_trabalho_old = PlanoTrabalho.objects.get(id=self.id)
            if plano_trabalho_old.aprovado_chefia:
                if plano_trabalho_old.aprovado_cigt:
                    raise ValidationError(
                        "Não é possível editar um Plano de Trabalho que já foi aprovado/reprovado pela Chefia Imediata e/ou CIGT")
        except PlanoTrabalho.DoesNotExist:
            ...

        if not self.aprovado_chefia:
            if self.aprovado_cigt:
                raise ValidationError(
                    "Não é possível fazer a Aprovação da CIGT antes da aprovação do Plano de Trabalho pela Chefia Imediata"
                )

    def get_lista_ano_mes_periodos_teletrabalho(self) -> typing.List[date]:
        """
        Método que retorna uma lista com os períodos
        do teletrabalho, mês a mês.
        """

        def diff_month(d1: date, d2: date) -> int:
            """
            Método que retorna a quantidade de meses
            entre duas datas"""

            return (d1.year - d2.year) * 12 + d1.month - d2.month

        def add_one_month(d: date) -> date:
            """
            Método que adiciona um mês em uma data.
            """
            if d.month + 1 > 12:
                return date(d.year+1, 1, d.day)
            return date(d.year, d.month + 1, d.day)

        periodos_ano_mes = set()
        for periodo in self.get_periodos_teletrabalho():
            data_inicial = periodo.data_inicio
            for _ in range(diff_month(periodo.data_fim, periodo.data_inicio) + 1):
                periodos_ano_mes.add(data_inicial)
                proximo_periodo = add_one_month(data_inicial)
                data_inicial = proximo_periodo

        #    for ano in range(periodo.data_inicio.year, periodo.data_fim.year + 1):
        #        for mes in range(periodo.data_inicio.month, periodo.data_fim.month + 1):
        #            ano_mes = date(ano, mes, 1)
        #            periodos_ano_mes.add(ano_mes)
        periodos_ano_mes = list(periodos_ano_mes)
        periodos_ano_mes.sort()
        return periodos_ano_mes

    def is_servidor_teletrabalho_ano_mes(self, anomes: str) -> bool:
        """
        Método que retorna se o servidor está em teletrabalho
        num dado ano/mes
        """
        periodos_teletrabalho = self.get_lista_ano_mes_periodos_teletrabalho()
        if anomes in set(periodos_teletrabalho):
            return True
        return False

    @classmethod
    def get_planos_trabalho_ano_mes(cls, anomes: str) -> list:
        """
        Método que retorna uma lista com todos os planos de trabalho
        de um dado período (anomes).
        """
        planos_trabalho = list()
        for p in cls.objects.order_by('manifestacao__servidor__nome'):
            if p.is_servidor_teletrabalho_ano_mes(anomes=anomes):
                planos_trabalho.append(p)
        return planos_trabalho

    def get_periodos_teletrabalho(self) -> models.QuerySet:
        periodos = PeriodoTeletrabalho.objects.filter(
            plano_trabalho=self)
        return periodos

    def get_atividades_plano_trabalho(self):
        atividades = AtividadesTeletrabalho.objects.filter(
            plano_trabalho_id=self.id)
        return atividades

    def get_context_docx(self):
        context = {
            'data': self.get_date(),
            'unidade': self.manifestacao.unidade,
            'setor': self.manifestacao.setor,
            'servidor': self.manifestacao.servidor,
            'funcao': self.manifestacao.funcao,
            'posto_trabalho': self.manifestacao.posto_trabalho,
            'chefia_imediata': self.manifestacao.chefia_imediata,
            'funcao_chefia': self.manifestacao.funcao_chefia,
            'posto_trabalho_chefia': self.manifestacao.posto_trabalho_chefia,
            'periodos_teletrabalho': self.get_periodos_teletrabalho(),
            'periodo_comparecimento': self.periodo_comparecimento,
            'periodo_acionamento': self.periodo_acionamento,
            'atividades': self.get_atividades_plano_trabalho(),

        }
        return context

    def __str__(self):
        return f'Plano de Trabalho: {self.manifestacao.servidor}'

    class Meta:
        verbose_name = 'Plano de Trabalho'
        verbose_name_plural = 'Chefia | Planos de Trabalho'


class AtividadesTeletrabalho(models.Model):
    # ao inves de fazer uma chave para o plano de trabalho
    # fazer uma chave para um período e deixar o período ligado ao plano de trabalho
    # inserir os campos de avaliação na própria atividade
    # desta forma, para cada período de um plano de trabalho
    # podemos avaliar as atividades individualmente

    plano_trabalho = models.ForeignKey(PlanoTrabalho, related_name="%(app_label)s_%(class)s_plano_trabalho", on_delete=models.CASCADE)  # noqa E501
    atividade = models.ForeignKey(ListaAtividades, related_name="%(app_label)s_%(class)s_atividade", on_delete=models.SET_NULL, null=True, blank=True)  # noqa E501
    meta_qualitativa = models.CharField(max_length=255, default='---', null=True, blank=True)  # noqa E501
    tipo_meta_quantitativa = models.ForeignKey(ListaIndicadoresMetricasTeletrabalho, related_name="%(app_label)s_%(class)s_metrica", on_delete=models.SET_NULL, null=True, blank=True)  # noqa E501
    meta_quantitativa = models.CharField(max_length=255)

    def __str__(self):
        return self.atividade.atividade

    class Meta:
        verbose_name = 'Atividade Teletrabalho'
        verbose_name_plural = 'Chefia | Atividades do Plano de Trabalho'


class Numeracao(models.Model):
    """
    Classe para registro de eventuais shifts de numeração.
    Permite implantar um controle de numeração de vários
    tipos de documentos, definindo um número inicial para cada um.
    """
    _TIPO_DOC = (
        ('parecer', 'Parecer'),
    )

    ano = models.IntegerField(default=timezone.now().year,
                              validators=[MinValueValidator(2023)])
    numero = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self) -> str:
        return f'{self.numero}/{self.ano}'

    @classmethod
    def get_ultimo_ano(cls) -> int:
        """
        Método que retorna o ano atual sincronizado
        com a numeração que está sendo gerada.
        """
        return datetime.now().year

    @classmethod
    def get_ultimo_numero(cls) -> int:
        """
        Função que retorna o número registrado por último.
        Caso não exista numeração para o setor, cria um
        objeto com o número 1.
        """

        try:
            obj = cls.objects.get(
                ano=datetime.now().year,
            )
            if obj:
                return obj.numero
        except cls.DoesNotExist:
            obj = Numeracao.objects.create(
            )
            return obj.numero

        raise KeyError("Tipo de documento informado não existe")

    class Meta:
        verbose_name = 'Numeração'
        verbose_name_plural = 'Admin | Numeração'

    @classmethod
    def update_ultimo_numero(cls) -> None:
        try:
            obj = cls.objects.get(
                ano=datetime.now().year)
            obj.numero += 1
            obj.save()

        except cls.DoesNotExist:
            cls.get_ultimo_numero()


class PeriodoTeletrabalho(models.Model):
    """
    Modelo para registrar os períodos de início e
    fim do regime de teletrabalho
    """
    plano_trabalho = models.ForeignKey(PlanoTrabalho, related_name="%(app_label)s_%(class)s_plano_trabalho", on_delete=models.CASCADE)  # noqa E501
    data_inicio = models.DateField(null=True, blank=True)
    data_fim = models.DateField(null=True, blank=True)

    def __str__(self):
        str_data_inicio = datetime.strftime(self.data_inicio, '%d/%m/%Y')
        str_data_fim = datetime.strftime(self.data_fim, '%d/%m/%Y')
        return f'{str_data_inicio} a {str_data_fim}'

    def year_month_normalize(self):
        """
        Método para salvar o período de teletrabalho começando sempre
        no primeiro dia da data_inicio apontada e terminando no último
        dia do mês da data_fim apontada
        """
        self.data_inicio = date(self.data_inicio.year,
                                self.data_inicio.month, 1)
        last_day_of_month = calendar.monthrange(
            self.data_fim.year, self.data_fim.month)[1]
        self.data_fim = date(self.data_fim.year,
                             self.data_fim.month, last_day_of_month)
        return self

    def clean(self):
        # normaliza o inicio e o fim do regime para o primeiro dia do primeiro mes
        # e último dia do último mês
        self.year_month_normalize()

        # verifica se a data_fim é maior que a data_inicio
        if not self.data_fim > self.data_inicio:
            raise ValidationError(
                "A data final não pode ser anterior à data inicial!")

    # USAR EM PRODUÇÃO
    #    # Impede a criação de plano de trabalho com regime retroativo
    #    if self.data_inicio < date.today():
    #        raise ValidationError(
    #            "Não é possível criar Plano de Trabalho para períodos pretéritos")

    class Meta:
        verbose_name = 'Período Teletrabalho'
        verbose_name_plural = 'Admin | Períodos Teletrabalho'


class DespachoCIGTAbstract(BaseModelGeneral):
    """
    Modelo abstrato para os despachos da CIGT
    """
    ano = models.IntegerField(default=datetime.now().year)
    numeracao = models.IntegerField(blank=True, null=True)
    membro_cigt = models.ForeignKey(ComissaoInterna, related_name="%(app_label)s_%(class)s_membro_cigt", on_delete=models.CASCADE, null=True)  # noqa E501

    def get_nome_presidente(self) -> str:
        presidente_cigt = ComissaoInterna.objects.filter(funcao='presidente').first()  # noqa E501
        return presidente_cigt.nome

    def get_membros_cigt(self) -> models.QuerySet:
        membros_cigt = ComissaoInterna.objects.filter(funcao='membro').order_by('nome')  # noqa E501
        return membros_cigt

    class Meta:
        abstract = True


class ParecerCIGT(DespachoCIGTAbstract):
    """
    Modelo para geração dos pareceres a respeito dos planos
    de trabalho e avaliações das chefias, de competência da
    comissão interna de gestão do teletrabalho.

    inicialmente, como no piloto a maiora dos planos de
    trabalho foram abertos fora do sistema, os campos serão
    texto puro e não referências aos modelos anteriormente
    criados.
    """
    plano_trabalho = models.ForeignKey(PlanoTrabalho, related_name="%(app_label)s_%(class)s_plano_trabalho", on_delete=models.CASCADE)  # noqa E501
    deferido = models.BooleanField(default=True)
    observacoes = models.TextField(null=True, blank=True)

    @classmethod
    def get_diff_months(cls, data_inicio, data_fim):
        """
        Método de classe que retorna quantos meses que existem entre
        duas datas.
        Se o teletrabalho é apenas durante um mês, retorna zero, se for
        durante 2 meses retorna 1, etc.
        """
        return (data_fim.year - data_inicio.year)*12 + data_fim.month - data_inicio.month  # noqa501

    def get_periodos_teletrabalho(self):
        """
        Método que retorna uma lista com ano/mes em
        que o servidor teve o plano de trabalho aprovado.
        """
        # NÃO ESTA FUNCIONANDO

        periodos = []
        periodos_plano = [p for p in PeriodoTeletrabalho.objects.filter(
            plano_trabalho=self.plano_trabalho)]

        for periodo in periodos_plano:
            data_inicio = periodo.data_inicio
            data_fim = periodo.data_fim
            qtd_meses_teletrabalho = ParecerCIGT.get_diff_months(
                data_inicio, data_fim)
            if qtd_meses_teletrabalho > 0:
                for _ in range(qtd_meses_teletrabalho + 1):
                    periodos.append(data_inicio)
                    if data_inicio.month < 12:
                        new_year = data_inicio.year
                        new_month = data_inicio.month + 1
                    else:
                        new_month = 1
                        new_year = data_inicio.year + 1
                    data_inicio = datetime(new_year,
                                           new_month,
                                           data_inicio.day)
                return periodos
            periodos.append(data_inicio)
            return periodos

    @classmethod
    def get_listagem_doe_by_periodo(cls):
        """
        Método para gerar listagem de servidores
        autorizados ao teletrabalho para publicação
        no DOE/PR com dados agrupados por período.
        """
        # NÃO ESTA FUNCIONANDO
        tabela_final_str = ''
        periodos = PeriodoTeletrabalho.objects.all()
        for periodo in periodos.order_by('data_inicio'):
            table = PrettyTable()
            tabela_final_str += f'\nPeríodo: {periodo}\n'
            table.field_names = ["SID", "RG", "NOME"]
            # pareceres = periodo.parecercigt_set.filter(deferido=True,
            #                                           publicado_doe=False).order_by('servidor')  # noqa E501
            pareceres = ParecerCIGT.objects.filter(deferido=True,
                                                       publicado_doe=False).order_by('servidor')  # noqa E501
            for parecer in pareceres:
                table.add_row([parecer.format_str_input('rg'), parecer.format_str_input('sid'), parecer.servidor.upper()])  # noqa E501
                table.align["SID"] = 'l'
                table.align["RG"] = 'l'
                table.align["NOME"] = 'l'
            tabela_final_str += table.get_formatted_string()

        return tabela_final_str

    @classmethod
    def get_listagem_doe_by_servidor(cls):
        """
        Método para gerar listagem de servidores
        autorizados ao teletrabalho para publicação
        no DOE/PR com dados agrupados por servidor.
        """
        # NÃO ESTA FUNCIONANDO
        table = PrettyTable()
        table.field_names = ["SID", "RG", "NOME", "PERÍODO(S)"]
        for parecer in cls.objects.filter(deferido=True,
                                          publicado_doe=False).order_by('servidor'):  # noqa E501
            periodos_parecer = []
            for periodo in parecer.periodo.all().order_by('data_inicio'):
                periodos_parecer.append(str(periodo))
            table.add_row([parecer.format_str_input('sid'),
                           parecer.format_str_input('rg'),
                           parecer.servidor.upper(),
                           '; '.join(periodos_parecer)])
        table.align["SID"] = 'l'
        table.align["RG"] = 'l'
        table.align["NOME"] = 'l'
        table.align["PERÍODO(S)"] = 'l'
        return table

    @classmethod
    def get_listagem_doe_csv(cls):
        """
        Método para gerar arquivo .csv
        que pode ser importado para o excel
        para envio ao DOE/PR.
        """
        # NÃO ESTA FUNCIONANDO
        path_csv_file = os.path.join(settings.MEDIA_ROOT,
                                     'doe.csv')
        with open(path_csv_file, 'w') as csvfile:
            for periodo in PeriodoTeletrabalho.objects.all().order_by('data_inicio', 'data_fim'):  # noqa E501
                csvfile.write(f'Período: {periodo}\n\n')

                csvfile.write('RG, SID, NOME\n')

                pareceres = periodo.parecercigt_set.filter(deferido=True,
                                                       publicado_doe=False).order_by('servidor')  # noqa E501
                for parecer in pareceres:
                    rg = parecer.format_str_input("rg")
                    sid = parecer.format_str_input("sid")
                    servidor = parecer.servidor.upper()
                    csvfile.write(f'{rg}, {sid}, {servidor}\n')

                csvfile.write('\n')

    def format_str_input(self, field: str) -> str:
        """
        Método que formata corretamente
        o RG e o e-protocolo com a máscara XX.XXX.XXX-X
        """
        # NÃO ESTA FUNCIONANDO
        if field not in ('rg', 'sid'):
            raise ValueError('field != "rg" ou "sid"')

        # remove puntuação
        no_punctuation_field = getattr(self.plano_trabalho.manifestacao.servidor, field).translate(
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

    def get_periodos_teletrabalho(self):
        periodos = PeriodoTeletrabalho.objects.filter(
            plano_trabalho=self.plano_trabalho)
        return periodos

    def clean(self):
        try:
            declaracao = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
                manifestacao=self.plano_trabalho.manifestacao).last()
            autorizacao_excecao = AutorizacoesExcecoes.objects.get(
                declaracao=declaracao)
            if not autorizacao_excecao.aprovado_gabinete:
                raise ValidationError(
                    "É preciso ter que o Diretor do Órgão aprove a excepcionalidade para concessão de teletrabalho a servidor com cargo de chefia ou direção!")
        except ObjectDoesNotExist:
            pass

    def get_excecao_cargo_chefia_direcao(self) -> bool:
        declaracao = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
            manifestacao=self.plano_trabalho.manifestacao).last()
        autorizacao_excecao = AutorizacoesExcecoes.objects.get(
            declaracao=declaracao)
        if not autorizacao_excecao.aprovado_gabinete:
            raise Exception("É preciso ter autorização do Diretor do Órgão!")
        if declaracao.cargo_chefia_direcao:
            return True
        return False

    def get_periodos_teletrabalho(self):
        periodos = PeriodoTeletrabalho.objects.filter(
            plano_trabalho=self.plano_trabalho)
        return periodos

    def get_context_docx(self):
        context = {
            'ano': self.ano,
            'numeracao': self.numeracao,
            'data': self.get_date(),
            'setor': self.plano_trabalho.manifestacao.setor,
            'pessoa': self.plano_trabalho.manifestacao.servidor,
            'rg': self.plano_trabalho.manifestacao.servidor.rg,
            'posto_trabalho': self.plano_trabalho.manifestacao.posto_trabalho,
            'periodos_teletrabalho': self.get_periodos_teletrabalho(),
            'deferido': self.deferido,
            'periodo_teletrabalho': self.get_periodos_teletrabalho(),
            'nome_presidente_cigt': self.get_nome_presidente(),
            'membros_cigt': self.get_membros_cigt(),
            'membro_cigt': str(self.membro_cigt),
            'excecao_cargo_chefia_direcao': self.get_excecao_cargo_chefia_direcao(),
        }
        return context

    def __str__(self) -> str:
        return f"Parecer CIGT n.{self.numeracao}-{self.ano}-{self.plano_trabalho.manifestacao.servidor}"

    class Meta:
        ordering = ('id', )
        verbose_name = 'Despacho CIGT Plano de Trabalho'
        verbose_name_plural = 'Despachos CIGT | Plano de Trabalho'


class ProtocoloAutorizacaoTeletrabalho(BaseModelGeneral):
    """
    Modelo para registrar os protocolos com as inclusões, alterações
    e exclusões do regime de teletrabalho
    """
    _CHOICES = (
        ('nao_publicado', 'Aguardando Publicação'),
        ('publicado', 'Publicado'),
        ('republicado', 'Republicado')
    )
    despacho_cigt = models.ForeignKey(ParecerCIGT, related_name="%(app_label)s_%(class)s_despacho_cigt", on_delete=models.CASCADE)  # noqa E501)
    sid = models.CharField(max_length=12, blank=True, null=True)
    publicado_doe = models.CharField(
        max_length=16, choices=_CHOICES, blank=True, null=True)

    def __str__(self) -> str:
        return f"Protocolo Autorização | Teletrabalho | {self.despacho_cigt.plano_trabalho.manifestacao.servidor.nome}"

    def clean(self):
        try:
            protocolo = ProtocoloAutorizacaoTeletrabalho.objects.get(
                id=self.id)
            if protocolo.publicado_doe != 'nao_publicado':
                raise ValidationError(
                    "Não é possível alterar um protocolo de autorização já publicado no DOE!")
        except ProtocoloAutorizacaoTeletrabalho.DoesNotExist:
            ...

    @classmethod
    def get_protocolos_aprovados_por_servidor(cls, servidor: User):
        """
        Método que retorna uma lista com os protocolos
        aprovados para o servidor.
        """
        manifestacoes = ManifestacaoInteresse.objects.filter(servidor=servidor)
        planos_trabalho = PlanoTrabalho.objects.filter(
            manifestacao__in=manifestacoes)
        pareceres_cigt = ParecerCIGT.objects.filter(
            plano_trabalho__in=planos_trabalho)
        # filtra todos os protocolos já aprovados
        protocolos_servidor = ProtocoloAutorizacaoTeletrabalho.objects.filter(
            despacho_cigt__in=pareceres_cigt)
        return protocolos_servidor

    @classmethod
    def get_periodos_aprovados_por_servidor(cls, servidor: User):
        """
        Método que retorna uma lista com todos os períodos
        aprovados para um servidor.
        """
        periodos = set()
        for protocolo in cls.get_protocolos_aprovados_por_servidor(servidor):
            for periodo in protocolo.despacho_cigt.plano_trabalho.get_lista_ano_mes_periodos_teletrabalho():
                periodos.add(periodo)
        periodos = list(periodos)
        periodos.sort()
        return periodos

    @classmethod
    def get_lista_ano_mes_periodo_teletrabalho_protocolos(cls) -> list:
        """
        Método que retorna uma lista ordenada com o conjunto
        das competências anomes em que servidores tiveram
        o regime de teletrabalho aprovado. 
        """
        periodos = set()
        for protocolo_autorizacao in cls.objects.all():
            periodos_plano = set(
                protocolo_autorizacao.despacho_cigt.plano_trabalho.get_lista_ano_mes_periodos_teletrabalho())
            for periodo_plano in periodos_plano:
                periodos.add(periodo_plano)
        periodos = list(periodos)
        periodos.sort()
        return periodos

    @classmethod
    def get_listagem_doe_csv(cls, commit_doe=False, tipo='inclusao') -> None:
        """
        Método para gerar arquivo .csv
        que pode ser importado para o excel
        para envio ao DOE/PR.

        - tipo: 'inclusao' ou 'exclusao'
        - commit_doe: altera o parametro publicado_doe para o protocolo.

        !!!! FUTURO: fazer uma função análoga que retorna um contexto um objeto
        do tipo abaixo para usar o docxtemplate para renderizar diretamente a portaria.
        [
            {
                'periodo': periodo,
                'nome': nome
                'rg'': rg
                'protocolo':
                'tipo': [inclusao/exclusao]
            },
            (...)
        ]

        !!! FUTURO: fazer com que a funcao retorne uma lista de objetos cujas chaves sejam as datas:

            {
                'inclusao/exclusao': {
                    '01/01/2023': {'nome': nome, 'rg': rg, 'periodo': periodo},
                    '01/02/2023': {'nome': nome, 'rg': rg, 'periodo': periodo},
                        (...)
                    }
            }
        """

        if tipo not in ('inclusao', 'exclusao'):
            raise ValueError('field != "rg" ou "sid"')

        filename = f'portaria_teletrabalho_doe_{date.today()}_{tipo}.csv'
        path_csv_file = os.path.join(settings.MEDIA_ROOT,
                                     filename)
        with open(path_csv_file, 'w') as csvfile:
            protocolos_publicados = set()
            controle_mensal_publicados = set()

            protocolos_json = {tipo: {}}

            for periodo in cls.get_lista_ano_mes_periodo_teletrabalho_protocolos():

                is_sid_pendente = False

                count_protocolos = 0

                protocolos_json[tipo][periodo] = []

                data_inicio = periodo.strftime("%d/%m/%Y")
                data_fim = f'{calendar.monthrange(periodo.year, periodo.month)[1]}/{periodo.month}/{periodo.year}'
                if tipo == 'inclusao':
                    texto_periodo_teletrabalho = f'INCLUSÕES : Período: {data_inicio} a {data_fim}\n\n'
                elif tipo == 'exclusao':
                    texto_periodo_teletrabalho = f'EXCLUSÕES : Período: {data_inicio} a {data_fim}\n\n'
                csvfile.write(texto_periodo_teletrabalho)
                csvfile.write("NOME, RG, PROTOCOLO\n")

                for controle_mensal in ControleMensalTeletrabalho.objects.filter(competencia=periodo):
                    plano_trabalho = controle_mensal.protocolo_autorizacao.despacho_cigt.plano_trabalho
                    # inclusão
                    if tipo == 'inclusao':
                        if controle_mensal.vigente:
                            if controle_mensal.publicado_doe == 'nao_publicado' or controle_mensal.publicado_doe == 'republicado':
                                # if controle_mensal.protocolo_autorizacao.publicado_doe == 'nao_publicado' or controle_mensal.protocolo_autorizacao.publicado_doe == 'republicado':
                                rg = plano_trabalho.manifestacao.servidor.rg_format()
                                servidor = plano_trabalho.manifestacao.servidor.nome.upper()
                                try:
                                    sid = controle_mensal.protocolo_autorizacao.sid_format()
                                    csvfile.write(f'{servidor}, {rg}, {sid}\n')

                                    protocolos_publicados.add(
                                        controle_mensal.protocolo_autorizacao)
                                    controle_mensal_publicados.add(
                                        controle_mensal
                                    )

                                    count_protocolos += 1

                                    protocolos_json[tipo][periodo].append(
                                        {
                                            'nome': servidor,
                                            'rg': rg,
                                            'protocolo': sid,
                                        }
                                    )

                                except AttributeError:
                                    is_sid_pendente = True
                                    print(
                                        f" [!] SID pendente para o Servidor: {servidor} -> [inclusão] teletrabalho não será publicado para {periodo}")
                                    return None
                    # exclusao

                    if tipo == 'exclusao':
                        if not controle_mensal.vigente:
                            # if controle_mensal.protocolo_autorizacao.publicado_doe == 'publicado':
                            if controle_mensal.publicado_doe == 'publicado':
                                rg = plano_trabalho.manifestacao.servidor.rg_format()
                                servidor = plano_trabalho.manifestacao.servidor.nome.upper()
                                try:
                                    sid = controle_mensal.protocolo_autorizacao.sid_format()
                                    csvfile.write(f'{servidor}, {rg}, {sid}\n')

                                    protocolos_publicados.add(
                                        controle_mensal.protocolo_autorizacao)
                                    controle_mensal_publicados.add(
                                        controle_mensal
                                    )

                                    count_protocolos += 1

                                    protocolos_json[tipo][periodo].append(
                                        {
                                            'nome': servidor,
                                            'rg': rg,
                                            'protocolo': sid,
                                        }
                                    )
                                except AttributeError:
                                    is_sid_pendente = True
                                    print(
                                        f" [!] SID pendente para o Servidor: {servidor} -> [inclusão] teletrabalho não será publicado para {periodo}")
                                    return None

                if count_protocolos == 0:
                    del (protocolos_json[tipo][periodo])

        protocolos_json['protocolos_publicados'] = protocolos_publicados
        protocolos_json['controle_mensal_publicados'] = controle_mensal_publicados

        return protocolos_json

    @classmethod
    def generate_portaria_publicacao(cls):
        """
        Método que cria um objeto PortariasPublicadasDOE
        com a portaria de publicação das autorizações e revogações
        do teletrabalho.
        """
        if cls.get_listagem_doe_csv(commit_doe=False, tipo='inclusao') is None:
            return None

        if cls.get_listagem_doe_csv(commit_doe=False, tipo='exclusao') is None:
            return None

        inclusoes = cls.get_listagem_doe_csv(
            commit_doe=False, tipo='inclusao')['inclusao']
        exclusoes = cls.get_listagem_doe_csv(
            commit_doe=False, tipo='exclusao')['exclusao']

        context = {
            'inclusoes': inclusoes,
            'exclusoes': exclusoes,
        }

        modelo_docx = ModeloDocumento.objects.get(nome_modelo='PORTARIA DOE')

        if inclusoes or exclusoes:

            obj = PortariasPublicadasDOE.objects.create(
                modelo=modelo_docx,
                has_inclusoes=True if context['inclusoes'] else False,
                has_exclusoes=True if context['exclusoes'] else False,
            )

            return obj

    def sid_format(self) -> str:
        """
        Método que formata corretamente
        o SID com a máscara XX.XXX.XXX-X
        """
        # remove puntuação
        no_punctuation_field = self.sid.translate(
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

    @classmethod
    def escala_teletrabalho(cls):
        ...

    def encaminha_pedido_avaliacao(self):
        """
        Método que verifica se é necessário encaminhar pedido
        de avaliação mensal por parte da chefia imediata.

        Retorna uma lista com as avalições encaminhadas.

        """
        def add_one_month(d: date) -> date:
            """
            Método que adiciona um mês em uma data.
            """
            if d.month + 1 > 12:
                return date(d.year+1, 1, d.day)
            return date(d.year, d.month + 1, d.day)

        avaliacoes_encaminhadas = []
        # pega periodos teletrabalho
        periodos_teletrabalho = self.despacho_cigt.plano_trabalho.get_lista_ano_mes_periodos_teletrabalho()
        # para cada periodo verifica se a competencia e posterior
        for periodo in periodos_teletrabalho:
            # data avaliacao = 1 mes depois do periodo
            data_avaliacao = add_one_month(periodo)
            if date.today() >= data_avaliacao:
                print(periodo, data_avaliacao)
                ano_avaliacao = periodo.year
                mes_avaliacao = periodo.month
                # verifica se ja foi encaminhado um pedido de avaliacao
                encaminhamentos_avaliacoes = DespachoEncaminhaAvaliacao.objects.filter(
                    Q(ano_avaliacao=ano_avaliacao) & Q(mes_avaliacao=mes_avaliacao) & Q(despacho_cigt=self.despacho_cigt))
                if not encaminhamentos_avaliacoes:
                    # cria encaminhamento de avaliacao
                    modelo_encaminhamento = ModeloDocumento.objects.get(nome_modelo="PROTOCOLO AUTORIZACAO TELETRABALHO")  # noqa E501
                    goat = User.objects.get(username='goat')
                    obj = DespachoEncaminhaAvaliacao.objects.create(
                        numeracao=Numeracao.get_ultimo_ano(),
                        ano_avaliacao=ano_avaliacao,
                        mes_avaliacao=mes_avaliacao,
                        despacho_cigt=self.despacho_cigt,
                        adicionado_por=goat,
                        modificado_por=goat,
                        modelo=modelo_encaminhamento
                    )
                    # cria avaliacao da chefia
                    modelo_avaliacao = ModeloDocumento.objects.get(
                        nome_modelo="AVALIACAO CHEFIA")
                    obj = AvaliacaoChefia.objects.create(
                        encaminhamento_avaliacao_cigt=obj,
                        adicionado_por=goat,
                        modificado_por=goat,
                        modelo=modelo_avaliacao)
                    avaliacoes_encaminhadas.append(obj)
        return avaliacoes_encaminhadas

    def verifica_avaliacoes(self):
        """
        Método que verifica se as chefias fizeram as avaliações encaminhadas
        """
        avaliacoes_pendentes = []
        encaminhamentos_avaliacoes_cigt = DespachoEncaminhaAvaliacao.objects.filter(
            despacho_cigt=self.despacho_cigt)
        print(
            f'avaliações encaminhadas: {self.despacho_cigt} - {encaminhamentos_avaliacoes_cigt}')
        for encaminhamento_avaliacao in encaminhamentos_avaliacoes_cigt:

            avaliacao = AvaliacaoChefia.objects.filter(
                encaminhamento_avaliacao_cigt=encaminhamento_avaliacao).first()
            print(
                f'encaminhamento: {encaminhamento_avaliacao} - avaliação {avaliacao}')
            if not avaliacao.atestado_cumprimento_metas:
                servidor = avaliacao.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.servidor
                mes_avaliacao = avaliacao.encaminhamento_avaliacao_cigt.mes_avaliacao
                ano_avaliacao = avaliacao.encaminhamento_avaliacao_cigt.ano_avaliacao
                print(
                    f'[-] Avaliação Pendente: {servidor}: {ano_avaliacao}/{mes_avaliacao}')
                avaliacoes_pendentes.append(avaliacao)
        return avaliacoes_pendentes

    def get_periodos_teletrabalho(self):
        periodos = PeriodoTeletrabalho.objects.filter(
            plano_trabalho=self.despacho_cigt.plano_trabalho)
        return periodos

    def get_declaracao_nao_enquadramento(self):
        declaracao_nao_enquadramento = DeclaracaoNaoEnquadramentoVedacoes.objects.get(
            manifestacao_id=self.despacho_cigt.plano_trabalho.manifestacao.id)
        return declaracao_nao_enquadramento

    def get_atividades_plano_trabalho(self):
        atividades = AtividadesTeletrabalho.objects.filter(
            plano_trabalho_id=self.despacho_cigt.plano_trabalho.id)
        return atividades

    def get_context_docx(self):
        context = {
            # manifestacao interesse
            'data': self.get_date(),
            'unidade': self.despacho_cigt.plano_trabalho.manifestacao.unidade,
            'setor': self.despacho_cigt.plano_trabalho.manifestacao.setor,
            'servidor': self.despacho_cigt.plano_trabalho.manifestacao.servidor,
            'funcao': self.despacho_cigt.plano_trabalho.manifestacao.funcao,
            # declaracao de nao enquadramento nas vedacoes
            'estagio_probatorio': self.get_declaracao_nao_enquadramento().estagio_probatorio,
            'cargo_chefia_direcao': self.get_declaracao_nao_enquadramento().cargo_chefia_direcao,
            'penalidade_disciplinar': self.get_declaracao_nao_enquadramento().penalidade_disciplinar,
            'justificativa_excecao': self.get_declaracao_nao_enquadramento().justificativa_excecao,
            # aprovacao gabinete
            'aprovado_gabinete': AutorizacoesExcecoes.objects.filter(declaracao=self.get_declaracao_nao_enquadramento()),
            # plano trabalho
            'posto_trabalho': self.despacho_cigt.plano_trabalho.manifestacao.posto_trabalho,
            'chefia_imediata': self.despacho_cigt.plano_trabalho.manifestacao.chefia_imediata,
            'funcao_chefia': self.despacho_cigt.plano_trabalho.manifestacao.funcao_chefia,
            'posto_trabalho_chefia': self.despacho_cigt.plano_trabalho.manifestacao.posto_trabalho_chefia,
            'periodos_teletrabalho': self.get_periodos_teletrabalho(),
            'periodo_comparecimento': self.despacho_cigt.plano_trabalho.periodo_comparecimento,
            'periodo_acionamento': self.despacho_cigt.plano_trabalho.periodo_acionamento,
            'atividades': self.get_atividades_plano_trabalho(),

        }
        return context

    class Meta:
        ordering = ('sid', )
        verbose_name = 'Protocolo Autorização Teletrabalho'
        verbose_name_plural = 'Chefias | Protocolos de Autorização Teletrabalho'


class PortariasPublicadasDOE(BaseModelMethods):
    """
    Este modelo faz o registro dos documentos gerados
    para a publicação das portarias relativas ao teletrabalho.
    """
    ano = models.IntegerField(null=True, blank=True)
    numero = models.IntegerField(null=True, blank=True)
    data_publicacao = models.DateField(null=True, blank=True)
    has_inclusoes = models.BooleanField()
    has_exclusoes = models.BooleanField()

    def __str__(self):
        return f'Portaria REPR {self.id}-{self.numero}/{self.ano}'

    def get_context_docx(self):
        inclusoes = ProtocoloAutorizacaoTeletrabalho.get_listagem_doe_csv(
            tipo='inclusao')
        exclusoes = ProtocoloAutorizacaoTeletrabalho.get_listagem_doe_csv(
            tipo='exclusao')

        for protocolo in inclusoes['protocolos_publicados']:
            protocolo.publicado_doe = 'publicado'
            protocolo.save()

        for protocolo in exclusoes['protocolos_publicados']:
            protocolo.publicado_doe = 'republicado'
            protocolo.save()

        for controle in inclusoes['controle_mensal_publicados']:
            controle.publicado_doe = 'publicado'
            controle.save()

        for controle in exclusoes['controle_mensal_publicados']:
            controle.publicado_doe = 'republicado'
            controle.save()

        context = {
            'inclusoes': inclusoes['inclusao'],
            'exclusoes': exclusoes['exclusao'],
        }

        return context

    class Meta:
        ordering = ('id', )
        verbose_name = 'CIGT | Portarias REPR DOE'
        verbose_name_plural = 'CIGT | Portarias REPR DOE'


class ControleMensalTeletrabalho(models.Model):
    """
    Modelo para controle dos servidores que estão em teletrabalho.
    Permite emissão de relatórios mensais e considera inclusões,
    alterações e exclusões de periodos.
    """
    _PATH_ARQ_ATUAL = os.path.join(
        settings.MEDIA_ROOT, 'relacao_servidores_periodo_atual.txt')
    _PATH_ARQ_OLD = os.path.join(
        settings.MEDIA_ROOT, 'relacao_servidores_periodo_old.txt')
    _CHOICES = (
        ('nao_publicado', 'Aguardando Publicação'),
        ('publicado', 'Publicado'),
        ('republicado', 'Republicado')
    )
    protocolo_autorizacao = models.ForeignKey(ProtocoloAutorizacaoTeletrabalho, related_name="%(app_label)s_%(class)s_protocolo_autorizacao", on_delete=models.CASCADE)  # noqa E501
    protocolo_alteracao = models.ForeignKey(ProtocoloAutorizacaoTeletrabalho, related_name="%(app_label)s_%(class)s_protocolo_alteracao", on_delete=models.CASCADE, null=True, blank=True)  # noqa E501
    competencia = models.DateField()
    vigente = models.BooleanField()
    publicado_doe = models.CharField(
        max_length=16, choices=_CHOICES, default='nao_publicado')

    def __str__(self) -> str:
        return f"CIGT | ControleMensalTeletrabalho-{self.protocolo_autorizacao}-{self.competencia}"

    @classmethod
    def get_periodos_aprovados_por_servidor(cls, servidor):
        """
        Método que retorna uma lista com todos os períodos
        aprovados para um servidor.
        """
        planos_trabalho = PlanoTrabalho.objects.filter(
            manifestacao__servidor=servidor)
        registros = cls.objects.filter(
            protocolo_autorizacao__despacho_cigt__plano_trabalho__in=planos_trabalho)
        periodos = set()
        for registro in registros:
            for periodo in registro.protocolo_autorizacao.despacho_cigt.plano_trabalho.get_lista_ano_mes_periodos_teletrabalho():
                periodos.add(periodo)
        periodos = list(periodos)
        periodos.sort()
        return periodos

    class Meta:
        verbose_name = "CIGT | Controle Mensal Teletrabalho"
        verbose_name_plural = "CIGT | Controle Mensal Teletrabalho"


@receiver(post_save, sender=ProtocoloAutorizacaoTeletrabalho, weak=False)
def controle_mensal_teletrabalho_callback(sender, **kwargs):
    """
    Função que faz o controle da Tabela ControleMensalTeletrabalho
    com base nas alterações de ProtocoloAutorizacaoTeletrabalho.

    Verifica se existe um protocolo já aprovado para o servidor.
    Verifica se houve alteração de períodos do teletrabalho para
    acrescentar ou remover o servidor da Portaria de autorização.

    """
    instance = kwargs['instance']
    created = kwargs['created']

    if created:

        servidor = instance.despacho_cigt.plano_trabalho.manifestacao.servidor
        planos_trabalho = PlanoTrabalho.objects.filter(
            manifestacao__servidor=servidor)
        pareceres_cigt = ParecerCIGT.objects.filter(
            plano_trabalho__in=planos_trabalho)
        # filtra todos os protocolos já aprovados
        protocolos_servidor = ProtocoloAutorizacaoTeletrabalho.get_protocolos_aprovados_por_servidor(
            servidor)
        # verifica o último protocolo aprovado
        # last_protocolo = protocolos_servidor.last()
        protocolo_atual = instance
        plano_trabalho_atual = instance.despacho_cigt.plano_trabalho
        # cria as entradas do novo protocolo na tabela ControleMensalTeletrabalho

        # tenho que escrever uma funcao que retorne um conjunto com os periodos ja aprovados da tabela de controlemensal

        periodos_ja_aprovados = ControleMensalTeletrabalho.get_periodos_aprovados_por_servidor(
            servidor)
        periodo_atual = plano_trabalho_atual.get_lista_ano_mes_periodos_teletrabalho()

        # precisamos verificar a necessidade de adicionar novas entradas na tabela
        # de controle mensal
        for periodo in periodo_atual:
            if not periodo in periodos_ja_aprovados:
                # situação em que o novo plano de trabalho tem um período que ainda
                # não está na tabela de controle mensal
                # nesse caso é preciso criar uma entrada na tabela de controle mensal
                print(
                    f'[+]{periodo} nao consta nos planos de trabalho já aprovados [ADICIONAR]')
                ControleMensalTeletrabalho.objects.create(
                    protocolo_autorizacao=protocolo_atual,
                    competencia=periodo,
                    vigente=True,
                )
            else:
                print(
                    f'[!]{periodo} consta no novo plano de trabalho e já consta em algum plano de trabalho antigo [NO ACTION]!')
                # situação em que o novo plano de trabalho tem um período que já
                # está na tabela de controle mensal
                # nesse caso, se a vigência estiver FALSE alteramos para TRUE, pois o período está no plano novo
                controle_mensal = ControleMensalTeletrabalho.objects.filter(
                    protocolo_autorizacao__in=protocolos_servidor).filter(competencia=periodo).first()
                controle_mensal.vigente = True
                controle_mensal.protocolo_alteracao = protocolo_atual
                controle_mensal.save()

        # precisamos verificar a necessidade de modificar uma entrada na tabel de controle
        # mensal.
        # se um novo plano de trabalho (instance) não contiver algum período já aprovado,
        # editamos a vigência do período

        for periodo in periodos_ja_aprovados:
            if not periodo in periodo_atual:
                print(
                    f'[!]{periodo} NÃO consta no novo plano de trabalho consta em algum plano de trabalho antigo [RETIRAR VIGÊNCIA]!')
                controle_mensal = ControleMensalTeletrabalho.objects.filter(
                    protocolo_autorizacao__in=protocolos_servidor).filter(competencia=periodo).first()
                controle_mensal.vigente = False
                controle_mensal.protocolo_alteracao = protocolo_atual
                controle_mensal.save()

        # for periodo in ProtocoloAutorizacaoTeletrabalho.get_periodos_aprovados_por_servidor(servidor):
            # if not ControleMensalTeletrabalho.objects.filter(protocolo_autorizacao=last_protocolo).filter(competencia=periodo):

            # for periodo_atual in plano_trabalho_atual.get_lista_ano_mes_periodos_teletrabalho():

            # for protocolo_servidor in protocolos_servidor:
                # if not ControleMensalTeletrabalho.objects.filter(protocolo_autorizacao=protocolo_servidor).filter(competencia=periodo):

        # itera todos os protocolos já aprovados para verificar se houve mudança de período
        """for protocolo in protocolos_servidor:
            # exclui o último protocolo
            if protocolo != instance:
                for periodo_anterior in protocolo.despacho_cigt.plano_trabalho.get_lista_ano_mes_periodos_teletrabalho():
                    # verifica se o período não consta no último protocolo
                    if not instance.despacho_cigt.plano_trabalho.is_servidor_teletrabalho_ano_mes(periodo_anterior):
                        print(f'{periodo_anterior} não consta no novo protocolo')
                        # tira a vigencia na tabela ControleMensalTeletralho
                        import ipdb
                        ipdb.set_trace()
                        controle_mensal = ControleMensalTeletrabalho.objects.filter(
                            protocolo_autorizacao=protocolo)
                        controle_mensal_periodo = controle_mensal.filter(
                            competencia=periodo_anterior).first()
                        controle_mensal_periodo.vigente = False
                        controle_mensal_periodo.protocolo_alteracao = protocolo_atual
                        controle_mensal_periodo.save()"""


class DespachoArquivamentoManifestacaoCIGT(DespachoCIGTAbstract):
    """
    Modelo para numeração de despachos de arquivamento dos encaminhamentos
    das manifestações de interesse dos servidores por parte das unidades.
    """
    sid = models.CharField(max_length=12)
    unidade = models.ForeignKey(Unidade, related_name="%(app_label)s_%(class)s_unidade", on_delete=models.CASCADE)  # noqa E501

    def get_context_docx(self):
        context = {
            'ano': self.ano,
            'numeracao': self.numeracao,
            'data': self.get_date(),
            'sid': self.sid,
            'unidade': self.unidade.nome,
            'membro_cigt': str(self.membro_cigt),
            'nome_presidente_cigt': self.get_nome_presidente()
        }

        return context

    def __str__(self) -> str:
        return f"Despacho Genérico CIGT n.{self.numeracao}-{self.ano}"

    class Meta:
        verbose_name = 'Despacho CIGT Arquivamento Manifestação'
        verbose_name_plural = 'Despachos CIGT | Arquivamento Manifestações'


class DespachoEncaminhaAvaliacao(DespachoCIGTAbstract):
    """
    Modelo para retorno dos protocolos para a avaliação
    das chefias
    """
    ano_avaliacao = models.IntegerField(default=timezone.now().year)
    mes_avaliacao = models.IntegerField(default=timezone.now().month)
    despacho_cigt = models.ForeignKey(ParecerCIGT, related_name="%(app_label)s_%(class)s_despacho_cigt", on_delete=models.CASCADE)  # noqa E501

    def get_context_docx(self):
        try:
            sid = ProtocoloAutorizacaoTeletrabalho.objects.get(
                despacho_cigt=self.despacho_cigt).sid
        except ProtocoloAutorizacaoTeletrabalho.DoesNotExist:
            raise Exception("Não há protocolo de autorização!")

        context = {
            'ano': self.ano,
            'sid': sid,
            'setor': self.despacho_cigt.plano_trabalho.manifestacao.setor,
            'numeracao': self.numeracao,
            'servidor': self.despacho_cigt.plano_trabalho.manifestacao.servidor,
            'num_despacho': self.despacho_cigt.numeracao,
            'ano_despacho': self.despacho_cigt.ano,
            'mes_avaliacao': self.mes_avaliacao,
            'ano_avaliacao': self.ano_avaliacao,
            'data': self.get_date(),
            'membro_cigt': str(self.despacho_cigt.membro_cigt),
            'nome_presidente_cigt': self.get_nome_presidente()
        }

        return context

    def __str__(self) -> str:
        return f"Despacho Encaminhamento Avaliação CIGT n.{self.numeracao}-{self.ano}-{self.mes_avaliacao}/{self.ano_avaliacao}"  # noqa E501

    class Meta:
        verbose_name = 'Despacho CIGT Encaminhamento Avaliação'
        verbose_name_plural = 'Despachos CIGT | Encaminhamentos Avaliações'


class AvaliacaoChefia(BaseModelGeneral):
    _CUMPRIMENTO_METAS = (
        ('1', 'Atesto que o servidor cumpriu integralmente todas as metas e/ou condições o Plano de Trabalho'),  # noqa E501
        ('2', 'Atesto que o servidor cumpriu as metas e/ou condições o Plano de Trabalho parcialmente'),  # noqa E501
        ('3', 'Atesto que o servidor não cumpriu as metas e/ou condições o Plano de Trabalho'),  # noqa E501
    )
    atestado_cumprimento_metas = models.CharField(choices=_CUMPRIMENTO_METAS,
                                                  max_length=255, null=True)
    justificativa_nao_cumprimento = models.TextField(blank=True, null=True)
    encaminhamento_avaliacao_cigt = models.ForeignKey(DespachoEncaminhaAvaliacao, related_name="%(app_label)s_%(class)s_encaminha_avaliacao", on_delete=models.CASCADE)  # noqa E501

    def get_atividades_plano_trabalho(self):
        plano_trabalho = self.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho
        atividades = AtividadesTeletrabalho.objects.filter(
            plano_trabalho_id=plano_trabalho.id)
        return atividades

    def get_context_docx(self):
        context = {
            'servidor': self.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.servidor,
            'chefia': self.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.chefia_imediata,
            'atividades': self.get_atividades_plano_trabalho(),
            'mes': self.encaminhamento_avaliacao_cigt.mes_avaliacao,
            'ano': self.encaminhamento_avaliacao_cigt.ano_avaliacao,
            'atestado_cumprimento_metas': self.atestado_cumprimento_metas,
            'justificativa_nao_cumprimento': self.justificativa_nao_cumprimento,  # noqa E501
        }
        return context

    def __str__(self):
        return f'Avaliação {self.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.servidor}'

    class Meta:
        verbose_name = 'Avaliação da Chefia'
        verbose_name_plural = 'Chefia | Avaliações da Chefia'


class DespachoRetornoAvaliacao(DespachoCIGTAbstract):
    """
    Modelo para retorno dos protocolos já contendo as
    avaliações das chefias imediatas.
    """
    _CUMPRIMENTO_METAS = (
        ('1', 'Servidor cumpriu integralmente todas as metas e/ou condições o Plano de Trabalho'),  # noqa E501
        ('2', 'Servidor cumpriu as metas e/ou condições o Plano de Trabalho parcialmente'),  # noqa E501
        ('3', 'Servidor não cumpriu as metas e/ou condições o Plano de Trabalho'),  # noqa E501
    )
    # mes = models.IntegerField(default=timezone.now().month)
    # despacho_cigt = models.ForeignKey(ParecerCIGT, related_name="%(app_label)s_%(class)s_despacho_cigt", on_delete=models.CASCADE)  # noqa E501
    avaliacao_chefia = models.ForeignKey(AvaliacaoChefia, related_name="%(app_label)s_%(class)s_avaliacao_chefia", on_delete=models.CASCADE)  # noqa E501
    # despacho_encaminhamento_avaliacao = models.ForeignKey(DespachoEncaminhaAvaliacao, related_name="%(app_label)s_%(class)s_encaminha_avaliacao", on_delete=models.CASCADE)  # noqa E501
    cumprimento_integral = models.CharField(choices=_CUMPRIMENTO_METAS, null=True, max_length=255)  # noqa E501

    def get_context_docx(self):
        try:
            sid = ProtocoloAutorizacaoTeletrabalho.objects.get(
                despacho_cigt=self.despacho_cigt).sid
        except ProtocoloAutorizacaoTeletrabalho.DoesNotExist:
            raise Exception("Não há protocolo de autorização!")
        context = {
            'ano': self.ano,
            'sid': sid,
            'setor': self.avaliacao_chefia.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.setor,
            'numeracao': self.numeracao,
            'servidor': self.avaliacao_chefia.encaminhamento_avaliacao_cigt.despacho_cigt.plano_trabalho.manifestacao.servidor,
            'cumprimento_integral': self.cumprimento_integral,
            'mes_avaliacao': self.avaliacao_chefia.encaminhamento_avaliacao_cigt.mes_avaliacao,
            'ano_avaliacao': self.avaliacao_chefia.encaminhamento_avaliacao_cigt.ano_avaliacao,
            'data': self.get_date(),
            'membro_cigt': str(self.membro_cigt),
            'nome_presidente_cigt': self.get_nome_presidente()
        }

        return context

    def __str__(self) -> str:
        mes_avaliacao = self.avaliacao_chefia.encaminhamento_avaliacao_cigt.mes_avaliacao
        ano_avaliacao = self.avaliacao_chefia.encaminhamento_avaliacao_cigt.ano_avaliacao
        return f"Despacho Retorno Avaliação CIGT n.{self.numeracao}-{mes_avaliacao}/{ano_avaliacao}"  # noqa E501

    class Meta:
        verbose_name = 'Despacho CIGT Retorno Avaliação'
        verbose_name_plural = 'Despachos CIGT | Retorno Avaliações'


class DespachoGenericoCIGT(DespachoCIGTAbstract):
    """
    Modelo para numeração de despachos genéricos
    da CIGT
    """
    interessada = models.CharField(max_length=255, blank=False)

    def get_context_docx(self):
        context = {
            'ano': self.ano,
            'numeracao': self.numeracao,
            'data': self.get_date(),
            'sid': self.sid,
            'interessada': self.interessada,
            'membro_cigt': str(self.membro_cigt),
            'nome_presidente_cigt': self.get_nome_presidente()
        }

        return context

    def __str__(self) -> str:
        return f"Despacho Genérico CIGT n.{self.numeracao}-{self.ano}"

    class Meta:
        verbose_name = 'Despacho CIGT Generico'
        verbose_name_plural = 'Despachos CIGT | Genéricos'


class ModelChangeLogsModel(models.Model):
    """
    Modelo criado para registrar logs das alterações
    de aprovação da chefia imediata no modelo ManifestacaoInteresse
    """
    user_id = models.BigIntegerField(null=False, blank=True, db_index=True)
    table_name = models.CharField(max_length=128, null=False, blank=True)
    table_row = models.CharField(max_length=128, null=False, blank=True)
    action = models.CharField(
        max_length=16, null=False, blank=True)  # saved or deleted
    old_value = models.CharField(max_length=128, null=True, blank=True)
    new_value = models.CharField(max_length=128, null=True, blank=True)
    timestamp = models.DateTimeField(null=False, blank=True)

    class Meta:
        verbose_name = "Logs autorizaçãos"
        verbose_name_plural = "Admin | Logs autorizações"


_TEMPLATES = [
    ParecerCIGT,
    DespachoArquivamentoManifestacaoCIGT,
    DespachoGenericoCIGT,
    DespachoEncaminhaAvaliacao,
    DespachoRetornoAvaliacao,
]

_LOG_MODELS = [
    ManifestacaoInteresse,
    DeclaracaoNaoEnquadramentoVedacoes,
]


for model in _TEMPLATES:
    @receiver(post_save, sender=model, weak=False)
    def numeracao_callback(sender, **kwargs):
        """
        Função criada para usar o Django Signals
        para alterar o modelo Numeracao automaticamente
        quando um novo item for criado nos modelos registrados
        em _TEMPLATES.
        """
        created = kwargs['created']
        if created:
            Numeracao.update_ultimo_numero()


@receiver(pre_save, sender=ManifestacaoInteresse, weak=False)
def log_aprovado_chefia_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals registrar a
    aprovação ou edição da aprovação da manifestação
    de interesse do servidor por parte da chefia imediata
    - modelo ManifestacaoInteresse
    """
    instance = kwargs['instance']
    try:
        for field in instance._meta.get_fields():
            old_instance = ManifestacaoInteresse.objects.get(
                id=instance.id)
            old_value = getattr(old_instance, field.name, None)
            new_value = getattr(instance, field.name, None)
            if new_value != old_value:
                data = {
                    'user_id': instance.modificado_por.id,
                    'table_name': sender._meta.model_name,
                    'table_row': field.name,
                    'action': 'changed',
                    'old_value': str(old_value),
                    'new_value': str(new_value),
                    'timestamp': timezone.now(),
                }
                ModelChangeLogsModel.objects.create(**data)
    except ManifestacaoInteresse.DoesNotExist:
        pass


@receiver(post_delete, sender=ManifestacaoInteresse, weak=False)
def log_deleta_manifestacao_interesse_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals registrar a
    exclusão de uma manifestação de interesse - modelo ManifestacaoInteresse
    """
    instance = kwargs['instance']

    for field in instance._meta.get_fields():
        data = {
            'user_id': instance.modificado_por.id,
            'table_name': instance._meta.model_name,
            'table_row': field.name,
            'action': 'deleted',
            'old_value': getattr(instance, field.name),
            'new_value': 'null',
            'timestamp': timezone.now(),
        }
        ModelChangeLogsModel.objects.create(**data)


@receiver(pre_save, sender=ManifestacaoInteresse, weak=False)
def altera_chefia_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals para
    atribuir automaticamente o grupo CHEFIAS para o usuário
    que for selecionado em chefia_imediata de um formulário
    do servidor quando o formulário é editado - 
    modelo ManifestacaoInteresse
    """

    instance = kwargs['instance']
    try:
        old_chefia_imediata = ManifestacaoInteresse.objects.get(
            id=instance.id).chefia_imediata
        if len(ManifestacaoInteresse.objects.filter(chefia_imediata=old_chefia_imediata)) < 2:
            chefias = Group.objects.get(name='CHEFIAS')
            chefias.user_set.remove(old_chefia_imediata)
    except ManifestacaoInteresse.DoesNotExist:
        pass


@receiver(pre_delete, sender=ManifestacaoInteresse, weak=False)
def deleta_chefia_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals para
    atribuir remover automativamente o grupo CHEFIAS para o usuário
    que deixar de ser apontado como chefia imediata na manifestação
    de interesse de servidor - modelo ManifestacaoInteresse
    """

    instance = kwargs['instance']
    old_chefia_imediata = ManifestacaoInteresse.objects.get(
        id=instance.id).chefia_imediata
    if len(ManifestacaoInteresse.objects.filter(chefia_imediata=old_chefia_imediata)) < 2:
        chefias = Group.objects.get(name='CHEFIAS')
        chefias.user_set.remove(old_chefia_imediata)


@receiver(post_save, sender=ManifestacaoInteresse, weak=False)
def adiciona_chefia_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals para
    atribuir automaticamente o grupo CHEFIAS para o usuário
    que for selecionado em chefia_imediata de um formulário
    do servidor - modelo ManifestacaoInteresse
    """

    # created = kwargs['created']
    instance = kwargs['instance']
    chefia_imediata = instance.chefia_imediata
    chefias = Group.objects.get(name='CHEFIAS')
    chefias.user_set.add(chefia_imediata)


@receiver(post_save, sender=PlanoTrabalho, weak=False)
def cria_despacho_cigt_aprovacao_plano_trabalho_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals para
    criar automaticamente o Despacho de Aprovação
    do Plano de Trabalho da CIGT quando o membro
    da CIGT seleciona aprovado_cigt=True

    Também cria automaticamente a ProtocoloAutorizacaoTeletrabalho
    que a chefia imediata deverá editar para colocar o sid com
    os formulários

    """
    created = kwargs['created']
    instance = kwargs['instance']
    if not created:
        if instance.aprovado_cigt:
            if not ParecerCIGT.objects.filter(plano_trabalho=instance):
                modelo = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
                # cria ParecerCIGT
                parecer = ParecerCIGT.objects.create(
                    plano_trabalho=instance,
                    modelo=modelo,
                    adicionado_por=instance.usuario_cigt_aprovacao,
                    modificado_por=instance.usuario_cigt_aprovacao,
                    numeracao=Numeracao.get_ultimo_numero()
                )
                # try except
                if ComissaoInterna.objects.get(user=instance.modificado_por):
                    parecer.membro_cigt = ComissaoInterna.objects.get(
                        user=instance.modificado_por)
                    parecer.save()
                # cria ProtocoloAutorizacaoTeletrabalho
                    modelo = ModeloDocumento.objects.get(nome_modelo="PROTOCOLO AUTORIZACAO TELETRABALHO")  # noqa E501
                    ProtocoloAutorizacaoTeletrabalho.objects.create(
                        despacho_cigt=parecer,
                        publicado_doe='nao_publicado',
                        modelo=modelo,
                        adicionado_por=instance.usuario_cigt_aprovacao,
                        modificado_por=instance.usuario_cigt_aprovacao)


@receiver(post_save, sender=DeclaracaoNaoEnquadramentoVedacoes, weak=False)
def autorizacao_diretor_teletrabalho_chefias_callback(sender, **kwargs):
    """
    Funcão que cria automaticamente a pendência de aprovação se
    uma declaracao é salva com cargo_chefia_direcao=False
    """
    instance = kwargs['instance']
    if not instance.cargo_chefia_direcao:
        if not AutorizacoesExcecoes.objects.filter(declaracao=instance):
            modelo = ModeloDocumento.objects.get(nome_modelo="APROVACAO EXCECAO DIRETOR")  # noqa E501
            AutorizacoesExcecoes.objects.create(
                declaracao=instance, modelo=modelo)


@receiver(post_save, sender=AvaliacaoChefia, weak=False)
def cria_despacho_retorno_avaliacao_chefias_callback(sender, **kwargs):
    """
    Função criada para usar o Django Signals para
    criar automaticamente o despacho de retorno de avaliações
    das chefias imediatas.
    """

    instance = kwargs['instance']

    modelo = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
    goat = User.objects.get(username='goat')

    try:
        despacho_retorno_avaliacao = DespachoRetornoAvaliacao.objects.get(
            avaliacao_chefia=instance)
        despacho_retorno_avaliacao.cumprimento_integral = instance.atestado_cumprimento_metas
        despacho_retorno_avaliacao.save()
    except DespachoRetornoAvaliacao.DoesNotExist:
        DespachoRetornoAvaliacao.objects.create(
            numeracao=Numeracao.get_ultimo_numero(),
            avaliacao_chefia=instance,
            cumprimento_integral=instance.atestado_cumprimento_metas,
            adicionado_por=goat,
            modificado_por=goat,
            modelo=modelo)
    # else:
    #    print('já existe')

# criar uma funcao que impede que a chefia imediata altere a avaliacao ja feita
# para ter uma nova avaliacao tem que deletar a antiga
