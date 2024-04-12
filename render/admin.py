import os
from typing import Any
from zipfile import ZipFile

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.db.models.query import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.http.request import HttpRequest
from unidecode import unidecode

from authentication.models import User

from .models import (FGT, AtividadesTeletrabalho, AutorizacoesExcecoes,
                     AvaliacaoChefia, Cargo, Chefia, ComissaoInterna,
                     ControleMensalTeletrabalho,
                     DeclaracaoNaoEnquadramentoVedacoes,
                     DespachoArquivamentoManifestacaoCIGT,
                     DespachoCIGTPlanoTrabalho, DespachoEncaminhaAvaliacao,
                     DespachoGenericoCIGT, DespachoRetornoAvaliacao,
                     ListaAtividades, ListaIndicadoresMetricasTeletrabalho,
                     ListaSistemasTeletrabalho, Lotacao, ManifestacaoInteresse,
                     ModelChangeLogsModel, ModeloDocumento, Numeracao,
                     PeriodoTeletrabalho, PlanoTrabalho,
                     PortariasPublicadasDOE, PostosTrabalho,
                     ProtocoloAutorizacaoTeletrabalho, Servidor, Setor,
                     Unidade)


@admin.action(description="Gerar protocolo DOCX")
def generate_protocolo_docx(modeladmin, request, queryset):
    """
    Gera o arquivo do protocolo .docx e faz o download.
    """
    tipo_doc = modeladmin.model._meta.verbose_name
    if queryset.count() == 1:
        obj = queryset.first()
        obj.render_docx_tpl(tipo_doc=tipo_doc)
        try:
            if os.path.exists(obj.docx.path):
                with open(obj.docx.path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
                    response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo(tipo_doc=tipo_doc)}'  # noqa E501
                    return response
        except ValueError:
            raise Exception('error generating docx file: associated docx not generated')  # noqa E501


@admin.action(description="Gerar arquivo DOCX")
def generate_docx(modeladmin, request, queryset):
    """
    Gera o arquivo .docx e faz o download.
    """
    tipo_doc = modeladmin.model._meta.verbose_name
    if queryset.count() == 1:
        obj = queryset.first()
        obj.render_docx_tpl(tipo_doc=tipo_doc)
        try:
            if os.path.exists(obj.docx.path):
                with open(obj.docx.path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
                    response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo(tipo_doc=tipo_doc)}'  # noqa E501
                    return response
        except ValueError:
            raise Exception('error generating docx file: associated docx not generated')  # noqa E501
    elif queryset.count() < 30:
        zip_file_path = os.path.join(
            settings.TEMP_FOLDER_ROOT,
            'download.zip')
        zip_file = ZipFile(zip_file_path, 'w')
        for obj in queryset:
            obj.render_docx_tpl(tipo_doc=tipo_doc)
            if os.path.exists(obj.docx.path):
                zip_file.write(obj.docx.path, os.path.basename(obj.docx.path))

        zip_file = open(zip_file_path, 'rb')
        response = HttpResponse(zip_file, content_type='application/force-download')  # noqa E501
        response['Content-Disposition'] = f'attachment; filename="Diversos_{tipo_doc}.zip"'  # noqa E501
        return response
    else:
        return HttpResponseBadRequest('Ação não Permitida -> Selecione menos de 30 arquivos')  # noqa E501


@admin.action(description="Publicação DOE")
def publica_doe(modeladmin, request, queryset):
    """
    Gera um arquivo .csv com informações para publicação
    no DOE e faz o download.
    """
    path_csv_file = os.path.join(settings.MEDIA_ROOT,
                                 'dinamic_publica_doe.csv')

    with open(path_csv_file, 'w', encoding='utf-8') as csvfile:

        for periodo in PeriodoTeletrabalho.objects.all().order_by('data_inicio', 'data_fim'):  # noqa E501
            pareceres = periodo.parecercigt_set.filter(deferido=True,
                                                    publicado_doe=False).order_by('servidor')  # noqa E501
            if pareceres:
                csvfile.write(f'Período: {periodo}\n\n')
                csvfile.write('NOME, RG, PROTOCOLO\n')

                for parecer in pareceres:
                    servidor = parecer.servidor
                    rg = parecer.format_str_input("rg")
                    protocolo = parecer.format_str_input("sid")
                    csvfile.write(f'{servidor}, {rg}, {protocolo}\n')
                    # parecer.publicado_doe = True
                    # parecer.save()
                csvfile.write('\n')

    try:
        if os.path.exists(path_csv_file):
            with open(path_csv_file, 'r', encoding='utf-8') as fh:
                response = HttpResponse(fh.read(), content_type='text/csv')  # noqa E501
                response['Content-Disposition'] = f'filename=lista-publica-doe.csv'  # noqa E501
                return response
    except ValueError:
        raise Exception('error generating csv file')  # noqa E501


class ManifestacaoInteresseAdmin(admin.ModelAdmin):
    list_display = ('lotacao_servidor', 'data_criacao', 'aprovado_chefia', 'adicionado_por', 'modificado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('lotacao_servidor', 'aprovado_chefia')
    # autocomplete_fields = (
    #     'unidade', 'setor', 'posto_trabalho', 'posto_trabalho_chefia')

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="MANIFESTACAO INTERESSE")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def delete_model(self, request, obj) -> None:
        if obj.aprovado_chefia:
            self.message_user(
                request, "Não é possível apagar uma manifestação já aprovada pela chefia imediata", level='error')
        else:
            return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for obj in queryset:
            if obj.aprovado_chefia:
                self.message_user(
                    request, "Não é possível apagar uma manifestação já aprovada pela chefia imediata", level='error')
                queryset = ManifestacaoInteresse.objects.none()
        return super().delete_queryset(request, queryset)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name='CIGT'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if request.user.groups.filter(name='GABINETE'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            if db_field.name == 'servidor':
                kwargs["queryset"] = User.objects.filter(id=request.user.id)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS'):
                    manifestacoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    servidores_id = {
                        p.servidor.id for p in manifestacoes_servidores}
                    servidores_id.add(request.user.id)
                    kwargs["queryset"] = User.objects.filter(
                        pk__in=servidores_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='GABINETE'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            if request.user.groups.filter(name='CHEFIAS'):
                manifestacaoes_servidores = ManifestacaoInteresse.objects.filter(
                    chefia_imediata=request.user)
                manifestacaoes_servidores_id = {
                    p.id for p in manifestacaoes_servidores}
                manifestacoes_chefia = ManifestacaoInteresse.objects.filter(
                    servidor=request.user)
                for m in manifestacoes_chefia:
                    manifestacaoes_servidores_id.add(m.id)
                queryset = ManifestacaoInteresse.objects.filter(
                    pk__in=manifestacaoes_servidores_id)
            return queryset
        queryset = ManifestacaoInteresse.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_readonly_fields(self, request, obj):
        if obj is not None:
            if obj.chefia_imediata == request.user:
                return ()
        return ('aprovado_chefia',)


class DeclaracaoNaoEnquadramentoVedacoesAdmin(admin.ModelAdmin):
    list_display = ('manifestacao', 'estagio_probatorio', 'cargo_chefia_direcao', 'penalidade_disciplinar', 'data_criacao', 'adicionado_por', 'modificado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('data', 'manifestacao', 'estagio_probatorio', 'cargo_chefia_direcao', 'penalidade_disciplinar', 'justificativa_excecao', )  # noqa E501

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="DECLARACAO NAO ENQUADRAMENTO VEDACOES")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def delete_model(self, request, obj) -> None:
        autorizacao = AutorizacoesExcecoes.objects.get(
            declaracao__manifestacao=obj.manifestacao)
        if autorizacao.aprovado_gabinete:
            self.message_user(
                request, "Não é possível apagar uma declaração que já foi aprovada/reprovada pela Direção", level='error')
        else:
            return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for obj in queryset:
            autorizacao = AutorizacoesExcecoes.objects.get(
                declaracao__manifestacao=obj.manifestacao)
            if autorizacao.aprovado_gabinete:
                self.message_user(
                    request, "Não é possível apagar uma manifestação já aprovada pela chefia imediata", level='error')
                queryset = DeclaracaoNaoEnquadramentoVedacoes.objects.none()
        return super().delete_queryset(request, queryset)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name='CIGT'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if request.user.groups.filter(name='GABINETE'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            if db_field.name == 'manifestacao':
                kwargs["queryset"] = ManifestacaoInteresse.objects.filter(adicionado_por=request.user)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS'):
                    # adicionar o proprio chefe e seus subordinados
                    manifestacaoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    manifestacao_chefia = ManifestacaoInteresse.objects.filter(
                        servidor=request.user)
                    manifestacoes_id = {
                        m.id for m in manifestacaoes_servidores}
                    for m in manifestacao_chefia:
                        manifestacoes_id.add(m.id)
                    kwargs['queryset'] = ManifestacaoInteresse.objects.filter(
                        pk__in=manifestacoes_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='GABINETE'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            queryset = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
                manifestacao__chefia_imediata=request.user)
            declaracoes_id = {declaracao.id for declaracao in queryset}
            try:
                declaracao_user = DeclaracaoNaoEnquadramentoVedacoes.objects.get(
                    manifestacao__servidor=request.user)
                declaracoes_id.add(declaracao_user.id)
            except DeclaracaoNaoEnquadramentoVedacoes.DoesNotExist:
                pass
            return DeclaracaoNaoEnquadramentoVedacoes.objects.filter(pk__in=declaracoes_id)
        queryset = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset


class AutorizacoesExcecoesAdmin(admin.ModelAdmin):
    list_display = ('declaracao', 'aprovado_gabinete', )
    actions = (generate_docx,)
    fields = ('aprovado_gabinete', 'declaracao')

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="APROVACAO EXCECAO DIRETOR")  # noqa E501
        obj.modelo = modelo
        obj.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def delete_model(self, request, obj) -> None:
        if obj.aprovado_gabinete:
            self.message_user(
                request, "Não é possível apagar uma autorização aprovada/reprovada pela Direção", level='error')
        else:
            return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for obj in queryset:
            if obj.aprovado_gabinete:
                self.message_user(
                    request, "Não é possível apagar uma autorização já aprovada pela chefia imediata", level='error')
                queryset = AutorizacoesExcecoes.objects.none()
        return super().delete_queryset(request, queryset)

    def get_readonly_fields(self, request, obj):
        if obj is not None:
            if request.user.groups.filter(name='GABINETE'):
                return ()
        return ('aprovado_gabinete',)


class ListaAtividadeAdmin(admin.ModelAdmin):
    search_fields = ('atividade', )


class PostosTrabalhoAdmin(admin.ModelAdmin):
    search_fields = ('setor', 'posto', )


class UnidadeAdmin(admin.ModelAdmin):
    search_fields = ('nome', )


class AtividadesTeletrabalhoInline(admin.TabularInline):
    model = AtividadesTeletrabalho
    fields = ('atividade', 'meta_qualitativa',
              'tipo_meta_quantitativa', 'meta_quantitativa', )


class PeriodoTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = ('plano_trabalho', 'data_inicio', 'data_fim')
    fields = ('plano_trabalho', 'data_inicio', 'data_fim')
    inlines = (AtividadesTeletrabalhoInline, )


class PeriodoTeletrabalhoInline(admin.TabularInline):
    model = PeriodoTeletrabalho


class AtividadesTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'atividade', )
    fields = ('periodo', 'atividade', 'meta_qualitativa', 'tipo_meta_quantitativa', 'meta_quantitativa', 'cumprimento', 'justificativa_nao_cumprimento')  # noqa E501
    readonly_fields = ()
    search_fields = ()
    autocomplete_fields = ('atividade', )

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = AtividadesTeletrabalho.objects.none()  # noqa E501
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name='CIGT'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            # mudar de Pessoa para User
            if db_field.name == 'plano_trabalho':
                kwargs["queryset"] = PlanoTrabalho.objects.filter(manifestacao__servidor=request.user)  # noqa E501
                """if request.user.groups.filter(name='CHEFIAS'):
                    manifestacoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    servidores_id = {
                        p.servidor.id for p in manifestacoes_servidores}
                    servidores_id.add(request.user.id)
                    kwargs["queryset"] = User.objects.filter(
                        pk__in=servidores_id)
            if db_field.name == 'manifestacao':
                kwargs["queryset"] = ManifestacaoInteresse.objects.filter(adicionado_por=request.user)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS')
                    # adicionar o proprio chefe e seus subordinados
                    manifestacaoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    manifestacao_chefia = ManifestacaoInteresse.objects.filter(
                        servidor=request.user)
                    manifestacoes_id = {
                        m.id for m in manifestacaoes_servidores}
                    for m in manifestacao_chefia:
                        manifestacoes_id.add(m.id)
                    kwargs['queryset'] = ManifestacaoInteresse.objects.filter(
                        pk__in=manifestacoes_id)"""
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class PlanoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('manifestacao', 'data_criacao', 'aprovado_chefia', 'aprovado_cigt', 'adicionado_por', 'modificado_por')  # noqa E501
    actions = (generate_docx, )
    fields = ('manifestacao', 'data', 'periodo_comparecimento', 'periodo_acionamento', 'sistemas', 'aprovado_chefia', 'aprovado_cigt')  # noqa E501
    autocomplete_fields = ()
    inlines = (PeriodoTeletrabalhoInline, )

    def save_model(self, request, obj, form, change):  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="PLANO DE TRABALHO")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)

        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user

        if request.user.groups.filter(name='CHEFIAS'):
            if obj.aprovado_chefia:
                obj.usuario_chefia_aprovacao = request.user

        if request.user.groups.filter(name='CIGT'):
            if obj.aprovado_cigt:
                obj.usuario_cigt_aprovacao = request.user
        return super().save_model(request, obj, form, change)

    def delete_model(self, request, obj) -> None:
        if obj.aprovado_chefia or obj.aprovado_cigt:
            self.message_user(
                request, "Não é possível apagar uma autorização aprovada/reprovada pela Chefia Imediata/CIGT", level='error')
        else:
            return super().delete_model(request, obj)

    def delete_queryset(self, request, queryset) -> None:
        for obj in queryset:
            if obj.aprovado_chefia or obj.aprovado_cigt:
                self.message_user(
                    request, "Não é possível apagar uma autorização aprovada/reprovada pela Chefia Imediata/CIGT", level='error')
                queryset = AutorizacoesExcecoes.objects.none()
        return super().delete_queryset(request, queryset)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            planos_servidores = PlanoTrabalho.objects.filter(
                manifestacao__chefia_imediata=request.user.id)
            planos_servidores_id = set()
            for plano in planos_servidores:
                planos_servidores_id.add(plano.id)
            planos_chefia = PlanoTrabalho.objects.filter(
                manifestacao__servidor=request.user)
            for p in planos_chefia:
                planos_servidores_id.add(p.id)
            return PlanoTrabalho.objects.filter(pk__in=planos_servidores_id)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        queryset = PlanoTrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def formfield_for_manytomany(self, db_field, request, **kwargs):  # noqa E501
        if request.user.groups.filter(name='CIGT'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            if db_field.name == 'atividade':
                kwargs["queryset"] = AtividadesTeletrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
            # if db_field.name == 'posto_trabalho':
            #     kwargs["queryset"] = PostosTrabalho.objects.exclude(tipo='PRESENCIAL') # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name='CIGT'):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            # mudar de Pessoa para User
            if db_field.name == 'servidor':
                kwargs["queryset"] = User.objects.filter(id=request.user.id)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS'):
                    manifestacoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    servidores_id = {
                        p.servidor.id for p in manifestacoes_servidores}
                    servidores_id.add(request.user.id)
                    kwargs["queryset"] = User.objects.filter(
                        pk__in=servidores_id)
            if db_field.name == 'manifestacao':
                kwargs["queryset"] = ManifestacaoInteresse.objects.filter(adicionado_por=request.user)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS'):
                    # adicionar o proprio chefe e seus subordinados
                    manifestacaoes_servidores = ManifestacaoInteresse.objects.filter(
                        chefia_imediata=request.user)
                    manifestacao_chefia = ManifestacaoInteresse.objects.filter(
                        servidor=request.user)
                    manifestacoes_id = {
                        m.id for m in manifestacaoes_servidores}
                    for m in manifestacao_chefia:
                        manifestacoes_id.add(m.id)
                    kwargs['queryset'] = ManifestacaoInteresse.objects.filter(
                        pk__in=manifestacoes_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_readonly_fields(self, request, obj):
        if request.user.groups.filter(name='CIGT'):
            return ('aprovado_chefia', )
        if request.user.groups.filter(name='CHEFIAS'):
            return ('aprovado_cigt', )
        return ('aprovado_cigt', 'aprovado_chefia')


class AvaliacaoChefiaAdmin(admin.ModelAdmin):
    list_display = ('encaminhamento_avaliacao_cigt', 'atestado_cumprimento_metas', 'data', 'data_criacao', 'adicionado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('encaminhamento_avaliacao_cigt', 'atestado_cumprimento_metas', 'justificativa_nao_cumprimento', )  # noqa E501

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="AVALIACAO CHEFIA")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # if not request.user.is_superuser:
        #    if db_field.name == 'plano_trabalho':
        #        kwargs["queryset"] = PlanoTrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
        #        if request.user.groups.filter(name='CIGT'):
        #            kwargs["queryset"] = PlanoTrabalho.objects.all()
        #        if request.user.groups.filter(name='CHEFIAS'):
        #            kwargs["queryset"] = PlanoTrabalho.objects.filter(
        #                manifestacao__chefia_imediata=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            despachos_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__chefia_imediata=request.user)
            queryset = AvaliacaoChefia.objects.filter(
                encaminhamento_avaliacao_cigt__despacho_cigt__in=despachos_cigt)
        return queryset


class DespachoCIGTPlanoTrabalhoAdmin(admin.ModelAdmin):
    list_display = ('plano_trabalho', 'ano', 'numeracao', 'data_criacao', 'membro_cigt')  # noqa E501
    actions = (generate_docx, publica_doe, )
    fields = ('plano_trabalho', 'membro_cigt', 'ano', 'data', 'deferido', )  # noqa E501
    autocomplete_fields = ()
    search_fields = ('plano_trabalho__servidor',)
    list_filter = ()

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append('')
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
        obj.modelo = modelo
        obj.adicionado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        queryset = DespachoCIGTPlanoTrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                'modelo': modelo,
                'membro_cigt': membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                'modelo': modelo,
            }


class ProtocoloAutorizacaoTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = ('despacho_cigt', 'sid', 'publicado_doe',
                    'adicionado_por', 'modificado_por')
    actions = (generate_protocolo_docx, )
    fields = ('sid', 'publicado_doe')

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="PROTOCOLO AUTORIZACAO TELETRABALHO")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            despachos_cigt_servidores = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__chefia_imediata=request.user)
            despachos_cigt = {
                despacho.pk for despacho in despachos_cigt_servidores}
            despachos_cigt_chefia = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__servidor=request.user)
            for despacho_cigt_chefia in despachos_cigt_chefia:
                despachos_cigt.add(despacho_cigt_chefia)
            queryset = ProtocoloAutorizacaoTeletrabalho.objects.filter(pk__in=despachos_cigt)  # noqa E501
        return queryset


class ControleMensalTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = ('protocolo_autorizacao', 'competencia',
                    'vigente', 'publicado_doe', 'get_publicado_doe')
    fields = ('protocolo_autorizacao', 'competencia',
              'vigente', 'protocolo_alteracao', 'publicado_doe',)

    def get_publicado_doe(self, obj) -> bool:
        return obj.protocolo_autorizacao.publicado_doe


class DespachoArquivamentoManifestacaoCIGTAdmin(admin.ModelAdmin):
    list_display = ('sid', 'numeracao', 'ano', 'unidade', 'data_criacao', 'data_edicao', 'adicionado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('sid', 'unidade', 'membro_cigt')  # noqa E501
    autocomplete_fields = ('unidade', )

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append('publicado_doe')
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="PARECER ARQUIVAMENTO MANIFESTACAO CIGT")  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.ano = Numeracao.get_ultimo_ano()
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = DespachoArquivamentoManifestacaoCIGT.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                'modelo': modelo,
                'membro_cigt': membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                'modelo': modelo,
            }


class DespachoEncaminhaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('despacho_cigt', 'numeracao', 'ano', 'ano_avaliacao', 'mes_avaliacao', 'data', 'data_criacao', 'data_edicao', 'adicionado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('despacho_cigt', 'ano_avaliacao', 'mes_avaliacao', 'membro_cigt', )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append('publicado_doe')
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO ENCAMINHA AVALIACAO CIGT")  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'despacho_cigt':
                kwargs["queryset"] = DespachoCIGTPlanoTrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        queryset = DespachoEncaminhaAvaliacao.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO ENCAMINHA AVALIACAO CIGT")  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                'modelo': modelo,
                'membro_cigt': membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                'modelo': modelo,
            }


class DespachoRetornoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('numeracao', 'ano', 'avaliacao_chefia', 'data', 'data_criacao', 'data_edicao', 'adicionado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('ano', 'avaliacao_chefia', 'cumprimento_integral', 'membro_cigt', )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append('publicado_doe')
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO RETORNO AVALIACAO CIGT")  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'despacho_cigt':
                kwargs["queryset"] = DespachoCIGTPlanoTrabalho.objects.filter(adicionado_por=request.user)  # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CIGT'):
            return super().get_queryset(request)
        queryset = DespachoRetornoAvaliacao.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO RETORNO AVALIACAO CIGT")  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                'modelo': modelo,
                'membro_cigt': membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                'modelo': modelo,
            }


class DespachoGenericoAdmin(admin.ModelAdmin):
    list_display = ('numeracao', 'interessada', 'data', 'data_criacao', 'data_edicao', 'adicionado_por')  # noqa E501
    actions = (generate_docx,)
    fields = ('interessada', 'membro_cigt', )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append('publicado_doe')
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO GENERICO CIGT")  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, 'adicionado_por'):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = DespachoGenericoCIGT.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(nome_modelo="DESPACHO GENERICO CIGT")  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                'modelo': modelo,
                'membro_cigt': membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                'modelo': modelo,
            }


"""class PessoaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'adicionado_por')
    exclude = ('adicionado_por', )
    autocomplete_fields = ('unidade', 'setor', 'posto_trabalho', )

    def nome(self, obj):
        return obj.servidor.nome

    def cargo(self, obj):
        return obj.servidor.cargo

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.adicionado_por = request.user
        obj.servidor.nome = unidecode(obj.servidor.nome).upper()
        obj.servidor.cargo = obj.servidor.cargo.upper()
        obj.funcao = obj.funcao.upper()
        obj.cidade = obj.cidade.upper()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'servidor':
                kwargs["queryset"] = User.objects.filter(id=request.user.id)  # noqa E501
                if request.user.groups.filter(name='CHEFIAS'):
                    servidores = Pessoa.objects.filter(
                        chefia_imediata=request.user)
                    users_id = set()
                    for s in servidores:
                        users_id.add(s.servidor.id)
                    users_id.add(request.user.id)
                    kwargs["queryset"] = User.objects.filter(pk__in=users_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name='CHEFIAS'):
            pessoa = Pessoa.objects.filter(
                chefia_imediata=request.user)
            users_id = set()
            for s in pessoa:
                users_id.add(s.id)
            if Pessoa.objects.filter(servidor=request.user):
                users_id.add(Pessoa.objects.get(servidor=request.user).id)
            queryset = Pessoa.objects.filter(pk__in=users_id)
            return queryset
        queryset = Pessoa.objects.filter(adicionado_por=request.user)  # noqa E501
        return queryset"""


class ModeloDocumentAdmin(admin.ModelAdmin):
    list_display = ('nome_modelo', 'template_docx')


class ComissaoInternaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'funcao')


class SetorAdmin(admin.ModelAdmin):
    search_fields = ('nome', )


class ModelChangeLogsModelAdmin(admin.ModelAdmin):
    list_display = ('table_name', 'user_id',
                    'table_row', 'action', 'old_value', 'new_value', 'timestamp')


class PortariasPublicadasDOEModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'data', 'ano', 'numero',
                    'data_publicacao', 'has_inclusoes', 'has_exclusoes',)
    fields = ('ano', 'numero', 'data_publicacao',
              'has_inclusoes', 'has_exclusoes', 'modelo', 'docx', 'pdf')


admin.site.register(ManifestacaoInteresse, ManifestacaoInteresseAdmin)
admin.site.register(PlanoTrabalho, PlanoTrabalhoAdmin)
admin.site.register(AvaliacaoChefia, AvaliacaoChefiaAdmin)
admin.site.register(ListaAtividades, ListaAtividadeAdmin)
admin.site.register(AtividadesTeletrabalho, AtividadesTeletrabalhoAdmin)
admin.site.register(DespachoCIGTPlanoTrabalho, DespachoCIGTPlanoTrabalhoAdmin)
admin.site.register(DespachoGenericoCIGT, DespachoGenericoAdmin)
admin.site.register(DespachoArquivamentoManifestacaoCIGT, DespachoArquivamentoManifestacaoCIGTAdmin)  # noqa E501
admin.site.register(ModeloDocumento, ModeloDocumentAdmin)
admin.site.register(ComissaoInterna, ComissaoInternaAdmin)
admin.site.register(Setor, SetorAdmin)
admin.site.register(PostosTrabalho, PostosTrabalhoAdmin)
admin.site.register(Unidade, UnidadeAdmin)
admin.site.register(DeclaracaoNaoEnquadramentoVedacoes, DeclaracaoNaoEnquadramentoVedacoesAdmin)  # noqa E501
admin.site.register(DespachoEncaminhaAvaliacao, DespachoEncaminhaAvaliacaoAdmin)  # noqa E501
admin.site.register(DespachoRetornoAvaliacao, DespachoRetornoAvaliacaoAdmin)

admin.site.register(ListaIndicadoresMetricasTeletrabalho)
admin.site.register(ListaSistemasTeletrabalho)
admin.site.register(Numeracao)
admin.site.register(PeriodoTeletrabalho)
admin.site.register(ModelChangeLogsModel, ModelChangeLogsModelAdmin)
admin.site.register(AutorizacoesExcecoes, AutorizacoesExcecoesAdmin)
admin.site.register(ProtocoloAutorizacaoTeletrabalho,
                    ProtocoloAutorizacaoTeletrabalhoAdmin)

admin.site.register(ControleMensalTeletrabalho,
                    ControleMensalTeletrabalhoAdmin)

admin.site.register(PortariasPublicadasDOE, PortariasPublicadasDOEModelAdmin)

admin.site.register(FGT)
admin.site.register(Servidor)
admin.site.register(Lotacao)
admin.site.register(Cargo)
admin.site.register(Chefia)
