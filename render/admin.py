import os
from zipfile import ZipFile

from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, HttpResponseBadRequest

from authentication.models import User

from .models import (
    FGT,
    AlterarAvaliacaoChefia,
    AtividadesTeletrabalho,
    AutorizacoesExcecoes,
    AvaliacaoChefia,
    Cargo,
    Chefia,
    ComissaoInterna,
    ControleMensalTeletrabalho,
    DeclaracaoNaoEnquadramentoVedacoes,
    DespachoArquivamentoManifestacaoCIGT,
    DespachoCIGTPlanoTrabalho,
    DespachoEncaminhaAvaliacao,
    DespachoGenericoCIGT,
    DespachoRetornoAvaliacao,
    ListaAtividades,
    ListaIndicadoresMetricasTeletrabalho,
    ListaSistemasTeletrabalho,
    Lotacao,
    ManifestacaoInteresse,
    ModelChangeLogsModel,
    ModeloDocumento,
    Numeracao,
    PeriodoTeletrabalho,
    PlanoTrabalho,
    PortariasPublicadasDOE,
    PostosTrabalho,
    ProtocoloAutorizacaoTeletrabalho,
    Servidor,
    Setor,
    Unidade,
)


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
                with open(obj.docx.path, "rb") as fh:
                    response = HttpResponse(
                        fh.read(), content_type="application/docx"
                    )  # noqa E501
                    response["Content-Disposition"] = (
                        f"filename={obj.gerar_nome_arquivo(tipo_doc=tipo_doc)}"  # noqa E501
                    )
                    return response
        except ValueError:
            raise Exception(
                "error generating docx file: associated docx not generated"
            )  # noqa E501
    elif queryset.count() < 30:
        zip_file_path = os.path.join(settings.TEMP_FOLDER_ROOT, "download.zip")
        zip_file = ZipFile(zip_file_path, "w")
        for obj in queryset:
            obj.render_docx_tpl(tipo_doc=tipo_doc)
            if os.path.exists(obj.docx.path):
                zip_file.write(obj.docx.path, os.path.basename(obj.docx.path))

        zip_file = open(zip_file_path, "rb")
        response = HttpResponse(
            zip_file, content_type="application/force-download"
        )  # noqa E501
        response["Content-Disposition"] = (
            f'attachment; filename="Diversos_{tipo_doc}.zip"'  # noqa E501
        )
        return response
    else:
        return HttpResponseBadRequest(
            "Ação não Permitida -> Selecione menos de 30 arquivos"
        )  # noqa E501


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    search_fields = ("nome",)
    ordering = ("nome",)


@admin.register(Chefia)
class ChefiaAdmin(admin.ModelAdmin):
    list_display = (
        "posto_trabalho",
        "posto_trabalho_chefia",
    )
    search_fields = (
        "posto_trabalho__setor__nome",
        "posto_trabalho_chefia__setor__nome",
    )


@admin.register(ComissaoInterna)
class ComissaoInternaAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "funcao",
    )
    search_fields = (
        "nome",
        "funcao",
    )


@admin.register(ListaAtividades)
class ListaAtividadesAdmin(admin.ModelAdmin):
    search_fields = ("atividade",)
    ordering = ("atividade",)


@admin.register(ListaIndicadoresMetricasTeletrabalho)
class ListaIndicadoresMetricasTeletrabalhoAdmin(admin.ModelAdmin):
    ordering = ("indicador",)


@admin.register(PostosTrabalho)
class PostosTrabalhoAdmin(admin.ModelAdmin):
    list_display = ("setor", "posto", "tipo", "chefia")
    list_filter = ("setor", "tipo", "chefia")
    search_fields = (
        "setor__nome",
        "posto",
    )
    ordering = ("setor__nome", "posto")


@admin.register(ModelChangeLogsModel)
class ModelChangeLogsModelAdmin(admin.ModelAdmin):
    list_display = (
        "table_name",
        "user_id",
        "table_row",
        "action",
        "old_value",
        "new_value",
        "timestamp",
    )


@admin.register(Lotacao)
class LotacaoAdmin(admin.ModelAdmin):
    list_display = ("servidor", "posto_trabalho", "atual")
    ordering = ("servidor", "data_inicio")
    search_fields = (
        "servidor__user__nome",
        "posto_trabalho__posto",
        "posto_trabalho__setor__nome",
    )


@admin.register(Numeracao)
class NumeracaoAdmin(admin.ModelAdmin):
    list_display = ("ano", "numero")


@admin.register(ManifestacaoInteresse)
class ManifestacaoInteresseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unidade",
        "setor",
        "lotacao_servidor",
        "data_criacao",
        "aprovado_chefia",
        "adicionado_por",
        "modificado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "lotacao_servidor",
        "lotacao_chefia",
        "aprovado_chefia",
        "justificativa_chefia",
        "adicionado_por",
        "modificado_por",
        "modelo",
        "docx",
        "pdf",
    )
    search_fields = (
        "lotacao_servidor__servidor__user__nome",
        "lotacao_servidor__servidor__user__rg",
        "lotacao_servidor__servidor__user__username",
    )
    ordering = ("-id",)
    actions = (generate_docx,)

    def unidade(self, obj) -> str:
        return obj.lotacao_servidor.posto_trabalho.setor.unidade.nome

    def setor(self, obj) -> str:
        return obj.lotacao_servidor.posto_trabalho.setor.nome


@admin.register(DeclaracaoNaoEnquadramentoVedacoes)
class DeclaracaoNaoEnquadramentoVedacoesAdmin(admin.ModelAdmin):
    list_display = (
        "manifestacao",
        "estagio_probatorio",
        "cargo_chefia_direcao",
        "penalidade_disciplinar",
        "data_criacao",
        "adicionado_por",
        "modificado_por",
    )
    actions = (generate_docx,)
    fields = (
        "data",
        "manifestacao",
        "estagio_probatorio",
        "cargo_chefia_direcao",
        "penalidade_disciplinar",
        "justificativa_excecao",
    )
    search_fields = (
        "manifestacao__lotacao_servidor__servidor__user__nome",
        "manifestacao__lotacao_servidor__servidor__user__rg",
        "manifestacao__lotacao_servidor__servidor__user__username",
    )


@admin.register(AutorizacoesExcecoes)
class AutorizacoesExcecoesAdmin(admin.ModelAdmin):
    list_display = (
        "unidade",
        "setor",
        "servidor",
        "aprovado_gabinete",
    )
    fields = ("aprovado_gabinete", "declaracao")
    actions = (generate_docx,)

    def unidade(self, obj) -> str:
        return (
            obj.declaracao.manifestacao.lotacao_servidor.posto_trabalho.setor.unidade.nome
        )

    def setor(self, obj) -> str:
        return obj.declaracao.manifestacao.lotacao_servidor.posto_trabalho.setor.nome

    def servidor(self, obj) -> str:
        return obj.declaracao.manifestacao.lotacao_servidor.servidor.user.nome


class UnidadeAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


class AtividadesTeletrabalhoInline(admin.TabularInline):
    model = AtividadesTeletrabalho
    fields = (
        "atividade",
        "meta_qualitativa",
        "tipo_meta_quantitativa",
        "meta_quantitativa",
    )


@admin.register(PeriodoTeletrabalho)
class PeriodoTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "unidade",
        "setor",
        "servidor",
        "plano_trabalho",
        "data_inicio",
        "data_fim",
    )
    fields = ("plano_trabalho", "data_inicio", "data_fim")
    inlines = (AtividadesTeletrabalhoInline,)

    def unidade(self, obj) -> str:
        return (
            obj.plano_trabalho.manifestacao.lotacao_servidor.posto_trabalho.setor.unidade.nome
        )

    def setor(self, obj) -> str:
        return (
            obj.plano_trabalho.manifestacao.lotacao_servidor.posto_trabalho.setor.nome
        )

    def servidor(self, obj) -> str:
        return obj.plano_trabalho.manifestacao.lotacao_servidor.servidor.user.nome


class PeriodoTeletrabalhoInline(admin.TabularInline):
    model = PeriodoTeletrabalho


class AtidadeTeletrabalhoInline(admin.TabularInline):
    model = AtividadesTeletrabalho


class AtividadesTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        "periodo",
        "atividade",
    )
    fields = (
        "periodo",
        "atividade",
        "meta_qualitativa",
        "tipo_meta_quantitativa",
        "meta_quantitativa",
        "cumprimento",
        "justificativa_nao_cumprimento",
    )  # noqa E501
    readonly_fields = ()
    search_fields = ()
    autocomplete_fields = ("atividade",)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = AtividadesTeletrabalho.objects.none()  # noqa E501
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.groups.filter(name="CIGT"):
            return super().formfield_for_foreignkey(db_field, request, **kwargs)
        if not request.user.is_superuser:
            # mudar de Pessoa para User
            if db_field.name == "plano_trabalho":
                kwargs["queryset"] = PlanoTrabalho.objects.filter(
                    manifestacao__servidor=request.user
                )  # noqa E501
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
    list_display = (
        "id",
        "unidade",
        "setor",
        "servidor",
        "data_criacao",
        "aprovado_chefia",
        "aprovado_cigt",
        "adicionado_por",
        "modificado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "manifestacao",
        "data",
        "periodo_comparecimento",
        "periodo_acionamento",
        "sistemas",
        "aprovado_chefia",
        "aprovado_cigt",
    )  # noqa E501
    autocomplete_fields = ()
    inlines = (PeriodoTeletrabalhoInline,)

    def unidade(self, obj) -> str:
        return obj.manifestacao.lotacao_servidor.posto_trabalho.setor.unidade.nome

    def setor(self, obj) -> str:
        return obj.manifestacao.lotacao_servidor.posto_trabalho.setor.nome

    def servidor(self, obj) -> str:
        return obj.manifestacao.lotacao_servidor.servidor.user.nome


# @admin.register(PeriodoTeletrabalho)
# class PeriodoTeletrabalhoAdmin(admin.ModelAdmin):
#     list_display = ("plano_trabalho", "data_inicio", "data_fim")
#     inlines = (AtidadeTeletrabalhoInline,)


class AvaliacaoChefiaAdmin(admin.ModelAdmin):
    list_display = (
        "encaminhamento_avaliacao_cigt",
        "atestado_cumprimento_metas",
        "data",
        "data_criacao",
        "adicionado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "encaminhamento_avaliacao_cigt",
        "atestado_cumprimento_metas",
        "justificativa_nao_cumprimento",
    )  # noqa E501

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="AVALIACAO CHEFIA"
        )  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
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
        if request.user.groups.filter(name="CIGT"):
            return super().get_queryset(request)
        if request.user.groups.filter(name="CHEFIAS"):
            despachos_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__chefia_imediata=request.user
            )
            queryset = AvaliacaoChefia.objects.filter(
                encaminhamento_avaliacao_cigt__despacho_cigt__in=despachos_cigt
            )
        return queryset


class DespachoCIGTPlanoTrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        "plano_trabalho",
        "ano",
        "numeracao",
        "data_criacao",
        "membro_cigt",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "plano_trabalho",
        "membro_cigt",
        "ano",
        "data",
        "deferido",
        "volume_docx",
    )  # noqa E501
    autocomplete_fields = ()
    search_fields = ("plano_trabalho__servidor",)
    list_filter = ()

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("")
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="PARECER PLANO DE TRABALHO CIGT"
        )  # noqa E501
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
        if request.user.groups.filter(name="CIGT"):
            return super().get_queryset(request)
        queryset = DespachoCIGTPlanoTrabalho.objects.filter(
            adicionado_por=request.user
        )  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(
            nome_modelo="PARECER PLANO DE TRABALHO CIGT"
        )  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                "modelo": modelo,
                "membro_cigt": membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                "modelo": modelo,
            }


class ProtocoloAutorizacaoTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        "despacho_cigt",
        "sid",
        "publicado_doe",
        "adicionado_por",
        "modificado_por",
    )
    fields = ("sid", "publicado_doe")

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="PROTOCOLO AUTORIZACAO TELETRABALHO"
        )  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name="CIGT"):
            return super().get_queryset(request)
        if request.user.groups.filter(name="CHEFIAS"):
            despachos_cigt_servidores = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__chefia_imediata=request.user
            )
            despachos_cigt = {despacho.pk for despacho in despachos_cigt_servidores}
            despachos_cigt_chefia = DespachoCIGTPlanoTrabalho.objects.filter(
                plano_trabalho__manifestacao__servidor=request.user
            )
            for despacho_cigt_chefia in despachos_cigt_chefia:
                despachos_cigt.add(despacho_cigt_chefia)
            queryset = ProtocoloAutorizacaoTeletrabalho.objects.filter(
                pk__in=despachos_cigt
            )  # noqa E501
        return queryset


class ControleMensalTeletrabalhoAdmin(admin.ModelAdmin):
    list_display = (
        "protocolo_autorizacao",
        "competencia",
        "vigente",
        "publicado_doe",
        "get_publicado_doe",
    )
    fields = (
        "protocolo_autorizacao",
        "competencia",
        "vigente",
        "protocolo_alteracao",
        "publicado_doe",
    )

    def get_publicado_doe(self, obj) -> bool:
        return obj.protocolo_autorizacao.publicado_doe


class DespachoArquivamentoManifestacaoCIGTAdmin(admin.ModelAdmin):
    list_display = (
        "sid",
        "numeracao",
        "ano",
        "unidade",
        "data_criacao",
        "data_edicao",
        "adicionado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = ("sid", "unidade", "membro_cigt")  # noqa E501
    autocomplete_fields = ("unidade",)

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("publicado_doe")
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="PARECER ARQUIVAMENTO MANIFESTACAO CIGT"
        )  # noqa E501
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.ano = Numeracao.get_ultimo_ano()
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = DespachoArquivamentoManifestacaoCIGT.objects.filter(
            adicionado_por=request.user
        )  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(
            nome_modelo="PARECER PLANO DE TRABALHO CIGT"
        )  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                "modelo": modelo,
                "membro_cigt": membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                "modelo": modelo,
            }


class DespachoEncaminhaAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "despacho_cigt",
        "numeracao",
        "ano",
        "ano_avaliacao",
        "mes_avaliacao",
        "data",
        "data_criacao",
        "data_edicao",
        "adicionado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "despacho_cigt",
        "ano_avaliacao",
        "mes_avaliacao",
        "membro_cigt",
    )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("publicado_doe")
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO ENCAMINHA AVALIACAO CIGT"
        )  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "despacho_cigt":
                kwargs["queryset"] = DespachoCIGTPlanoTrabalho.objects.filter(
                    adicionado_por=request.user
                )  # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name="CIGT"):
            return super().get_queryset(request)
        queryset = DespachoEncaminhaAvaliacao.objects.filter(
            adicionado_por=request.user
        )  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO ENCAMINHA AVALIACAO CIGT"
        )  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                "modelo": modelo,
                "membro_cigt": membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                "modelo": modelo,
            }


class DespachoRetornoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = (
        "numeracao",
        "ano",
        "avaliacao_chefia",
        "data",
        "data_criacao",
        "data_edicao",
        "adicionado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "ano",
        "avaliacao_chefia",
        "cumprimento_integral",
        "membro_cigt",
    )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("publicado_doe")
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO RETORNO AVALIACAO CIGT"
        )  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == "despacho_cigt":
                kwargs["queryset"] = DespachoCIGTPlanoTrabalho.objects.filter(
                    adicionado_por=request.user
                )  # noqa E501
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        if request.user.groups.filter(name="CIGT"):
            return super().get_queryset(request)
        queryset = DespachoRetornoAvaliacao.objects.filter(
            adicionado_por=request.user
        )  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO RETORNO AVALIACAO CIGT"
        )  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                "modelo": modelo,
                "membro_cigt": membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                "modelo": modelo,
            }


class DespachoGenericoAdmin(admin.ModelAdmin):
    list_display = (
        "numeracao",
        "interessada",
        "data",
        "data_criacao",
        "data_edicao",
        "adicionado_por",
    )  # noqa E501
    actions = (generate_docx,)
    fields = (
        "interessada",
        "membro_cigt",
    )  # noqa E501

    def get_readonly_fields(self, request, *args, **kwargs):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("publicado_doe")
        return fields

    def save_model(self, request, obj, form, change) -> None:  # noqa E501
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO GENERICO CIGT"
        )  # noqa E501
        # posteriormente, adicione implemente a formatacao do RG, SID
        # e a aplicação do unidecode no nome para remover acentuação
        # que atrapalha na ordenação
        obj.modelo = modelo
        instance = form.save(commit=False)
        if not hasattr(instance, "adicionado_por"):
            obj.adicionado_por = request.user
        instance.modificado_por = request.user
        if not change:
            obj.numeracao = Numeracao.get_ultimo_numero()
        return super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            return super().get_queryset(request)
        queryset = DespachoGenericoCIGT.objects.filter(
            adicionado_por=request.user
        )  # noqa E501
        return queryset

    def get_changeform_initial_data(self, request):
        modelo = ModeloDocumento.objects.get(
            nome_modelo="DESPACHO GENERICO CIGT"
        )  # noqa E501
        try:
            membro_cigt = ComissaoInterna.objects.get(user=request.user)
            return {
                "modelo": modelo,
                "membro_cigt": membro_cigt,
            }
        except ComissaoInterna.DoesNotExist:
            return {
                "modelo": modelo,
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


@admin.register(ModeloDocumento)
class ModeloDocumentoAdmin(admin.ModelAdmin):
    list_display = ("nome_modelo", "template_docx")


class SetorAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


class PortariasPublicadasDOEModelAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "data",
        "ano",
        "numero",
        "data_publicacao",
        "has_inclusoes",
        "has_exclusoes",
    )
    fields = (
        "ano",
        "numero",
        "data_publicacao",
        "has_inclusoes",
        "has_exclusoes",
        "modelo",
        "docx",
        "pdf",
    )


admin.site.register(PlanoTrabalho, PlanoTrabalhoAdmin)
admin.site.register(AvaliacaoChefia, AvaliacaoChefiaAdmin)

admin.site.register(AtividadesTeletrabalho, AtividadesTeletrabalhoAdmin)
admin.site.register(DespachoCIGTPlanoTrabalho, DespachoCIGTPlanoTrabalhoAdmin)
admin.site.register(DespachoGenericoCIGT, DespachoGenericoAdmin)
admin.site.register(
    DespachoArquivamentoManifestacaoCIGT, DespachoArquivamentoManifestacaoCIGTAdmin
)  # noqa E501

admin.site.register(Setor, SetorAdmin)
admin.site.register(Unidade, UnidadeAdmin)

admin.site.register(
    DespachoEncaminhaAvaliacao, DespachoEncaminhaAvaliacaoAdmin
)  # noqa E501
admin.site.register(DespachoRetornoAvaliacao, DespachoRetornoAvaliacaoAdmin)


admin.site.register(ListaSistemasTeletrabalho)

admin.site.register(
    ProtocoloAutorizacaoTeletrabalho, ProtocoloAutorizacaoTeletrabalhoAdmin
)

admin.site.register(ControleMensalTeletrabalho, ControleMensalTeletrabalhoAdmin)

admin.site.register(PortariasPublicadasDOE, PortariasPublicadasDOEModelAdmin)

admin.site.register(FGT)
admin.site.register(Servidor)

admin.site.register(AlterarAvaliacaoChefia)
