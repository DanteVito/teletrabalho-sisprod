import calendar
import os
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from render.forms import (AtividadeCumprimentoForm, AtividadesTeletrabalhoForm,
                          AtividadesTeletrabalhoFormSet,
                          AutorizacoesExcecoesAprovaForm,
                          AutorizacoesExcecoesForm,
                          AvaliacaoChefiaFinalizaForm, AvaliacaoChefiaForm,
                          DeclaracaoNaoEnquadramentoVedacoesForm, LotacaoForm,
                          ManifestacaoInteresseAprovadoChefiaForm,
                          ManifestacaoInteresseForm, PeriodoTeletrabalhoForm,
                          PeriodoTeletrabalhoFormSet, PlanoTrabalhoForm,
                          PlanoTrabalhoFormAprovadoChefiaForm,
                          PlanoTrabalhoFormAprovadoCIGTForm,
                          PortariaDoeEditForm,
                          ProtocoloAutorizacaoTeletrabalhoAprovaForm,
                          ProtocoloAutorizacaoTeletrabalhoForm, ServidorForm,
                          UserForm)
from render.models import (AtividadesTeletrabalho, AutorizacoesExcecoes,
                           AvaliacaoChefia, ComissaoInterna,
                           ControleMensalTeletrabalho,
                           DeclaracaoNaoEnquadramentoVedacoes,
                           DespachoCIGTPlanoTrabalho, ManifestacaoInteresse,
                           ModeloDocumento, Numeracao, PeriodoTeletrabalho,
                           PlanoTrabalho, PortariasPublicadasDOE,
                           ProtocoloAutorizacaoTeletrabalho, Servidor)


@login_required
def home(request):
    context = {
    }
    return render(request, 'webapp/pages/home.html', context)


@login_required
def dados_cadastrais(request):
    user_groups = request.user.groups.all()
    # form_user = UserForm(instance=request.user)
    servidor = Servidor.objects.get(user__id=request.user.id)
    form_servidor = ServidorForm(user=request.user, instance=servidor)

    if request.method == 'POST':
        form = ServidorForm(request.POST, instance=servidor, user=request.user)

        if form.is_valid():
            form.save()
            return redirect(reverse('webapp:servidor'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        # 'form_user': form,
        'form_servidor': form_servidor,
        'user_groups': user_groups,
    }

    return render(request, 'webapp/pages/dados-cadastrais.html', context)


@login_required
def manifestacao_interesse(request):
    servidor = Servidor.objects.get(user=request.user)
    check_dados = servidor.check_dados()
    if check_dados:
        return redirect(reverse('webapp:dados_cadastrais'))

    manifestacoes_servidor = ManifestacaoInteresse.objects.filter(
        lotacao__servidor__user=request.user)

    context = {
        'manifestacoes_servidor': manifestacoes_servidor,
    }
    return render(request, 'webapp/pages/manifestacao-interesse.html', context)


@login_required
def manifestacao_interesse_create(request):
    form = LotacaoForm(user=request.user)
    
    if request.method == 'POST':
        form = LotacaoForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.servidor = request.user
            obj.adicionado_por = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='MANIFESTACAO INTERESSE')
            obj.save()
            messages.info(request, "Manifestação cadastrada com sucesso!")
            return redirect(reverse('webapp:manifestacao_interesse'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)
    context = {
        'form': form,
        'tipo_form': 'create',
    }
    return render(request, 'webapp/pages/manifestacao-interesse-form.html', context)


@login_required
def manifestacao_interesse_edit(request, pk):
    # garante que somente o proprio usuário possa
    # editar a manifestação que ele cadastrou
    try:
        instance = ManifestacaoInteresse.objects.get(
            pk=pk, servidor=request.user)
    except ManifestacaoInteresse.DoesNotExist:
        return HttpResponseBadRequest("")

    form = ManifestacaoInteresseForm(instance=instance, user=request.user)

    if request.method == 'POST':
        form = ManifestacaoInteresseForm(
            request.POST, instance=instance, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.servidor = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='MANIFESTACAO INTERESSE')
            obj.save()
            messages.info(request, "Manifestação alterada com sucesso!")
            return redirect(reverse('webapp:manifestacao_interesse'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'tipo_form': 'edit',
        'form': form,
    }
    return render(request, 'webapp/pages/manifestacao-interesse-form.html', context)


@login_required
def manifestacao_interesse_aprovado_chefia(request, pk):
    # garante que apenas o usuário registrado como chefia
    # imediata na manifestacação possa aprovar a manifestação
    try:
        manifestacao = ManifestacaoInteresse.objects.get(
            pk=pk, chefia_imediata=request.user)
    except ManifestacaoInteresse.DoesNotExist:
        return HttpResponseBadRequest("proibido")

    servidor = manifestacao.servidor
    form_instance = ManifestacaoInteresseForm(
        instance=manifestacao, user=servidor)

    form = ManifestacaoInteresseAprovadoChefiaForm(
        instance=manifestacao)

    if request.method == 'POST':
        form = ManifestacaoInteresseAprovadoChefiaForm(
            request.POST, instance=manifestacao)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()
            return redirect(reverse('webapp:chefia_imediata_analisar_manifestacoes'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'manifestacao': manifestacao,
        'form': form,
        'form_instance': form_instance,
    }
    return render(request, 'webapp/pages/manifestacao-interesse-aprovado-chefia.html', context)


@login_required
def manifestacao_interesse_delete(request, pk):
    # garante que somente o proprio usuário possa
    # excluir a manifestação que ele cadastrou
    try:
        instance = ManifestacaoInteresse.objects.get(
            pk=pk, servidor=request.user)
    except ManifestacaoInteresse.DoesNotExist:
        return HttpResponseBadRequest()

    if instance.aprovado_chefia:
        messages.warning(
            request, "Não é possível deletar uma Manifestação de Interesse já aprovada/reprovada!")
    else:
        if instance.adicionado_por == request.user:
            instance.delete()
            messages.info(request, "Manifestação excluída com sucesso!")
        else:
            return HttpResponseBadRequest("")
    return redirect(reverse('webapp:manifestacao_interesse'))


@login_required
def declaracao_nao_enquadramento(request):
    servidor = Servidor.objects.get(user=request.user)
    check_dados = servidor.check_dados()
    if check_dados:
        return redirect(reverse('webapp:dados_cadastrais'))
    declaracoes = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        manifestacao__servidor=request.user)
    autorizacoes_excecoes = AutorizacoesExcecoes.objects.filter(
        declaracao__in=declaracoes)
    pk_autorizacoes_excecoes = set([a.pk for a in autorizacoes_excecoes])
    pk_declaracoes_autorizacoes = set([
        a.declaracao.pk for a in autorizacoes_excecoes])
    pk_declaracoes = set([d.pk for d in declaracoes])
    pk_declaracoes_autorizadas = pk_declaracoes.difference(
        pk_declaracoes_autorizacoes)
    declaracoes_autorizadas = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        pk__in=pk_declaracoes_autorizadas)

    declaracoes_pendentes_gab = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        pk__in=pk_declaracoes_autorizacoes)

    context = {
        'declaracoes': declaracoes_autorizadas,
        'autorizacoes_excecoes': autorizacoes_excecoes,
        'declaracoes_autorizacoes': zip(declaracoes_pendentes_gab, autorizacoes_excecoes)
    }

    return render(request, 'webapp/pages/declaracao-nao-enquadramento.html', context)


@login_required
def declaracao_nao_enquadramento_create(request):
    form = DeclaracaoNaoEnquadramentoVedacoesForm(user=request.user)
    if request.method == 'POST':
        form = DeclaracaoNaoEnquadramentoVedacoesForm(
            request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            manifestacao = form.cleaned_data['manifestacao']
            # garante que apenas manifestações de interesse do próprio
            # usuário possam ser utilizadas
            if not manifestacao in ManifestacaoInteresse.objects.filter(servidor=request.user):
                return HttpResponseBadRequest("not allowed")
            obj.adicionado_por = request.user
            obj.modificado_por = request.user
            modelo_aprovacao_excecao = ModeloDocumento.objects.get(nome_modelo="APROVACAO EXCECAO DIRETOR")  # noqa E501
            modelo_declaracao = ModeloDocumento.objects.get(
                nome_modelo='DECLARACAO NAO ENQUADRAMENTO VEDACOES')
            obj.modelo = modelo_declaracao
            obj.save()

            if not obj.cargo_chefia_direcao:
                if not AutorizacoesExcecoes.objects.filter(declaracao=obj):
                    AutorizacoesExcecoes.objects.create(
                        declaracao=obj, modelo=modelo_aprovacao_excecao)

            messages.info(request, "Declaração cadastrada com sucesso!")
            return redirect(reverse('webapp:declaracao_nao_enquadramento'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'tipo_form': 'create',
        'form': form
    }
    return render(request, 'webapp/pages/declaracao-nao-enquadramento-form.html', context)


@login_required
def declaracao_nao_enquadramento_edit(request, pk):
    # garante que somente o proprio usuário possa
    # editar a declaração que ele cadastrou
    try:
        instance = DeclaracaoNaoEnquadramentoVedacoes.objects.get(
            pk=pk, manifestacao__servidor=request.user)
    except DeclaracaoNaoEnquadramentoVedacoes.DoesNotExist:
        return HttpResponseBadRequest()

    form = DeclaracaoNaoEnquadramentoVedacoesForm(
        instance=instance, user=request.user)
    if request.method == 'POST':
        form = DeclaracaoNaoEnquadramentoVedacoesForm(
            request.POST, instance=instance, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()

            if not obj.cargo_chefia_direcao:
                if not AutorizacoesExcecoes.objects.filter(declaracao=obj):
                    modelo_aprovacao_excecao = ModeloDocumento.objects.get(nome_modelo="APROVACAO EXCECAO DIRETOR")  # noqa E501
                    AutorizacoesExcecoes.objects.create(
                        declaracao=obj, modelo=modelo_aprovacao_excecao)

            messages.info(request, "Declaração alterada com sucesso!")
            return redirect(reverse('webapp:declaracao_nao_enquadramento'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'tipo_form': 'edit',
        'form': form
    }
    return render(request, 'webapp/pages/declaracao-nao-enquadramento-form.html', context)


@login_required
def declaracao_nao_enquadramento_delete(request, pk):
    # garante que apenas o próprio usuário possa
    # deletar a declaração que ele criou.
    try:
        instance = DeclaracaoNaoEnquadramentoVedacoes.objects.get(
            pk=pk, manifestacao__servidor=request.user)
    except DeclaracaoNaoEnquadramentoVedacoes.DoesNotExist:
        return HttpResponseBadRequest()

    try:
        AutorizacoesExcecoes.objects.get(
            declaracao=instance)
        messages.warning(request, "Não é possível excluir a Declaração de Não Enquadramento\
                enquanto houver um Pedido de Autorização da Direção pendente\
                para ocupante de cargo de chefia ou direção!")
        return redirect(reverse('webapp:declaracao_nao_enquadramento'))
    except AutorizacoesExcecoes.DoesNotExist:
        ...
        instance.delete()
        messages.info(request, "Manifestação excluída com sucesso!")
    return redirect(reverse('webapp:declaracao_nao_enquadramento'))


@login_required
def plano_trabalho(request):
    servidor = Servidor.objects.get(user=request.user)
    check_dados = servidor.check_dados()
    if check_dados:
        return redirect(reverse('webapp:dados_cadastrais'))
    if not ManifestacaoInteresse.objects.filter(
            servidor=request.user):
        messages.info(
            request, "É necessário cadastrar a Manifestação de Interesse antes de cadastrar o Plano de Trabalho!")
        return redirect(reverse('webapp:manifestacao_interesse'))
    if not DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
            manifestacao__servidor=request.user):
        messages.info(
            request, "É necessário cadastrar a Declaração de Não Enquadramento nas Vedações Legais antes de cadastrar o Plano de Trabalho!")
        return redirect(reverse('webapp:declaracao_nao_enquadramento'))

    planos_trabalho = PlanoTrabalho.objects.filter(
        manifestacao__servidor=request.user)
    context = {
        'planos_trabalho': planos_trabalho
    }
    return render(request, 'webapp/pages/plano-trabalho.html', context)


@login_required
def plano_trabalho_create(request):
    # escrever validações para garantir que apenas o próprio
    # usuário possa cadastrar um plano de trabalho para ele mesmo,
    # assim como a sua chefia imediata

    last_manifestacao = ManifestacaoInteresse.objects.filter(
        servidor=request.user).last()
    if not last_manifestacao.aprovado_chefia:
        messages.info(
            request, "É necessário ter a Manifestação de Interesse aprovada antes de cadastrar o Plano de Trabalho!")
        return redirect(reverse('webapp:plano_trabalho'))

    instance = PlanoTrabalho()

    form = PlanoTrabalhoForm(
        user=request.user)
    # PeriodoTeletrabalhoFormSet = inlineformset_factory(
    #     PlanoTrabalho, PeriodoTeletrabalho, fields=("data_inicio", "data_fim")
    # )
    periodos_formset = PeriodoTeletrabalhoFormSet()
    # AtividadesTeletrabalhoFormSet = inlineformset_factory(
    #     PeriodoTeletrabalho, AtividadesTeletrabalho, fields=(
    #         "periodo", "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa", "cumprimento", "justificativa_nao_cumprimento",)
    # )
    atividades_formset = AtividadesTeletrabalhoFormSet()
    if request.method == 'POST':
        form = PlanoTrabalhoForm(request.POST, user=request.user)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.servidor = request.user
            obj.adicionado_por = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='PLANO DE TRABALHO')
            obj.save()

            # when using commit=False we must call save_m2m()
            # for many to many fields

            form.save_m2m()

            # associa todos os períodos ao plano de trabalho salvo
            periodos_formset = PeriodoTeletrabalhoFormSet(
                request.POST, instance=obj)

            if periodos_formset.is_valid():
                periodos_salvos = periodos_formset.save(commit=False)
                periodos_salvos_set = set()

                for periodo_salvo in periodos_salvos:
                    for periodo in periodo_salvo.year_months_periodo():
                        periodos_salvos_set.add(periodo)

                del (periodos_salvos)

                periodos_salvos_set = list(periodos_salvos_set)
                periodos_salvos_set.sort()
            else:
                # temos que validar que a data final de cada período
                # é maior que a data inicial de cada período.
                # aqui criamos um redirecionamento para exibir o erro
                return HttpResponse('Data final não pode ser anterior à data inicial!')

            for periodo in periodos_salvos_set:
                last_day_month = calendar.monthrange(
                    periodo.year, periodo.month)[1]
                data_fim = date(periodo.year, periodo.month, last_day_month)
                obj = PeriodoTeletrabalho.objects.create(
                    plano_trabalho=periodos_formset.instance,
                    data_inicio=periodo,
                    data_fim=data_fim
                )
                # associa todas as atividades a todos os períodos salvos
                atividades_formset = AtividadesTeletrabalhoFormSet(
                    request.POST, instance=obj)

                if atividades_formset.is_valid():
                    atividades_formset.save()
                else:
                    # se escrevermos validações para o formset
                    # das atividades, redirecionamos aqui.
                    return HttpResponse('Problema na validação das atividades!')

            messages.info(request, "Plano de Trabalho cadastrado com sucesso!")
            return redirect(reverse('webapp:plano_trabalho'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'tipo_form': 'create',
        'form': form,
        'periodos_formset': periodos_formset,
        'atividades_formset': atividades_formset,
    }
    return render(request, 'webapp/pages/plano-trabalho-form.html', context)


@login_required
def plano_trabalho_edit(request, pk):
    # garante que apenas o próprio usuário
    # possa alterar o plano de trabalho que ele cadastrou
    # posteriormente expandir para autorizar a chefia
    # imediata

    try:
        instance = PlanoTrabalho.objects.get(
            pk=pk, manifestacao__servidor=request.user)
        if instance.aprovado_chefia:
            return redirect(reverse('webapp:plano_trabalho'))
    except PlanoTrabalho.DoesNotExist:
        return HttpResponseBadRequest("not allowed")

    periodos_teletrabalho = PeriodoTeletrabalho.objects.filter(
        plano_trabalho=instance)
    form = PlanoTrabalhoForm(
        instance=instance, user=instance.manifestacao.servidor)
    periodos_formset = PeriodoTeletrabalhoFormSet()
    if request.method == 'POST':
        form = PlanoTrabalhoForm(
            request.POST, instance=instance, user=instance.manifestacao.servidor)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()

            # when using commit=False we must call save_m2m()
            # for many to many fields

            form.save_m2m()

            messages.info(request, "Plano de Trabalho alterado com sucesso!")
            return redirect(reverse('webapp:plano_trabalho'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    periodos_teletrabalho = PeriodoTeletrabalho.objects.filter(
        plano_trabalho=instance)
    atividades_teletrabalho = AtividadesTeletrabalho.objects.filter(
        periodo__in=periodos_teletrabalho)

    context = {
        'tipo_form': 'edit',
        'periodos_teletrabalho': periodos_teletrabalho,
        'form': form,
        'periodos_formset': periodos_formset,
        'periodos_teletrabalho': periodos_teletrabalho,
        'atividades_teletrabalho': atividades_teletrabalho,
    }
    return render(request, 'webapp/pages/plano-trabalho-form.html', context)


@login_required
def plano_trabalho_aprovado_chefia(request, pk):
    # garante que apenas o usuário registrado como chefia
    # imediata na manifestacação possa aprovar o plano de trabalho
    try:
        plano_trabalho = PlanoTrabalho.objects.get(
            pk=pk, manifestacao__chefia_imediata=request.user)
    except PlanoTrabalho.DoesNotExist:
        return HttpResponseBadRequest("proibido")

    form_instance = PlanoTrabalhoForm(
        instance=plano_trabalho, user=plano_trabalho.manifestacao.servidor)
    form = PlanoTrabalhoFormAprovadoChefiaForm(instance=plano_trabalho)
    if request.method == 'POST':
        form = PlanoTrabalhoFormAprovadoChefiaForm(
            request.POST, instance=plano_trabalho)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()
            return redirect(reverse('webapp:chefia_imediata_analisar_planos_trabalho'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    periodos_teletrabalho = PeriodoTeletrabalho.objects.filter(
        plano_trabalho=plano_trabalho)
    atividades_teletrabalho = AtividadesTeletrabalho.objects.filter(
        periodo__in=periodos_teletrabalho)

    context = {
        'plano_trabalho': plano_trabalho,
        'form': form,
        'form_instance': form_instance,
        'periodos_teletrabalho': periodos_teletrabalho,
        'atividades_teletrabalho': atividades_teletrabalho,

    }
    return render(request, 'webapp/pages/plano-trabalho-aprovado-chefia.html', context)


@login_required
def plano_trabalho_aprovado_cigt(request, pk):
    # garante que apenas o usuário registrado como do grupo CIGT
    # possa aprovar o plano de trabalho

    # substituir o signals
    # DespachoCIGTPlanoTrabalho
    # ProtocoloAutorizacaoTeletrabalho

    # criar o despachocigtplanodetrabalho e o protocoloautorizacaoteletrabralho

    try:
        membro_cigt = ComissaoInterna.objects.get(
            user=request.user)
    except ComissaoInterna.DoesNotExist:
        return HttpResponse("USUÁRIO NÃO PERTENCE A TABELA COMISSÃO INTERNA CIGT")

    if request.user.groups.filter(name="CIGT"):
        plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
        form_instance = PlanoTrabalhoForm(
            instance=plano_trabalho, user=request.user)
        form = PlanoTrabalhoFormAprovadoCIGTForm(instance=plano_trabalho)
        if request.method == 'POST':
            form = PlanoTrabalhoFormAprovadoCIGTForm(
                request.POST, instance=plano_trabalho)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.modificado_por = request.user
                obj.usuario_cigt_aprovacao = request.user
                obj.save()

                # eliminar o signals para criar os objetos após a
                # aprovação da CIGT. fazer com que os objetos sejam
                # criados aqui na view.
                if obj.aprovado_cigt == 'aprovado':

                    if not DespachoCIGTPlanoTrabalho.objects.filter(plano_trabalho=obj):
                        modelo_plano_trabalho = ModeloDocumento.objects.get(nome_modelo="PARECER PLANO DE TRABALHO CIGT")  # noqa E501
                        modelo_protocolo_autorizacao = ModeloDocumento.objects.get(nome_modelo="PROTOCOLO AUTORIZACAO TELETRABALHO")  # noqa E501

                        # cria DespachoCIGTPlanoTrabalho
                        despacho_cigt_plano_trabalho = DespachoCIGTPlanoTrabalho.objects.create(
                            plano_trabalho=obj,
                            modelo=modelo_plano_trabalho,
                            adicionado_por=request.user,
                            modificado_por=request.user,
                            membro_cigt=membro_cigt,
                            numeracao=Numeracao.get_ultimo_numero()
                        )
                        # cria ProtocoloAutorizacaoTeletrabalho
                        ProtocoloAutorizacaoTeletrabalho.objects.create(
                            despacho_cigt=despacho_cigt_plano_trabalho,
                            publicado_doe='nao_publicado',
                            modelo=modelo_protocolo_autorizacao,
                            adicionado_por=request.user,
                            modificado_por=request.user)
                return redirect(reverse('webapp:cigt_analisar_planos_trabalho'))

            for _, error_list in form.errors.items():
                for e in error_list:
                    messages.error(request, e)

        periodos_teletrabalho = PeriodoTeletrabalho.objects.filter(
            plano_trabalho=plano_trabalho)
        atividades_teletrabalho = AtividadesTeletrabalho.objects.filter(
            periodo__in=periodos_teletrabalho)

        context = {
            'plano_trabalho': plano_trabalho,
            'form': form,
            'form_instance': form_instance,
            'periodos_teletrabalho': periodos_teletrabalho,
            'atividades_teletrabalho': atividades_teletrabalho,

        }
        return render(request, 'webapp/pages/plano-trabalho-aprovado-cigt.html', context)
    return HttpResponseBadRequest("proibido")


@login_required
def plano_trabalho_delete(request, pk):
    # escrever as validações para que apenas o próprio usuário e a chefia
    # imediata possam deletar o plano de trabalho cadastrado por ambos.
    # usar o messages.

    plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    if not plano_trabalho.aprovado_chefia:
        plano_trabalho.delete()

    return redirect(reverse('webapp:plano_trabalho'))


@login_required
def periodo_teletrabalho(request, pk):
    # note que pk é a chave primária do plano de trabalho
    # PeriodoTeletrabalhoFormSet = inlineformset_factory(
    #     PlanoTrabalho, PeriodoTeletrabalho, fields=("data_inicio", "data_fim")
    # )
    # plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    # formset = PeriodoTeletrabalhoFormSet(instance=plano_trabalho)
    # if request.method == 'POST':
    #     formset = PeriodoTeletrabalhoFormSet(
    #         request.POST, instance=plano_trabalho)
    #     if formset.is_valid():
    #         formset.save()
    #         plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    #         # formset = PeriodoTeletrabalhoFormSet(instance=plano_trabalho)
    #         return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': pk}))
    # context = {
    #     'formset': formset,
    # }
    obj = PeriodoTeletrabalho.objects.get(pk=pk)
    form = PeriodoTeletrabalhoForm(instance=obj)

    if request.method == 'POST':
        form = PeriodoTeletrabalhoForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': obj.plano_trabalho_id}))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'form': form
    }
    return render(request, 'webapp/pages/periodo-teletrabalho-form.html', context)


@login_required
def periodo_teletrabalho_delete(request, pk):
    instance = PeriodoTeletrabalho.objects.get(pk=pk)
    if instance.plano_trabalho.aprovado_chefia:
        messages.error(
            request, "Não é possível excluir um Período de um Plano de Trabalho já aprovado/reprovado!")
    else:
        instance.delete()
    return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': instance.plano_trabalho_id}))


@login_required
def atividade_teletrabalho(request, pk):
    # note que pk é a chave primária do plano de trabalho
    # AtividadesTeletrabalhoFormSet = inlineformset_factory(
    #     PlanoTrabalho, AtividadesTeletrabalho, fields=(
    #         "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa")
    # )
    # plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    # formset = AtividadesTeletrabalhoFormSet(instance=plano_trabalho)
    # if request.method == 'POST':
    #     formset = AtividadesTeletrabalhoFormSet(
    #         request.POST, instance=plano_trabalho)
    #     if formset.is_valid():
    #         formset.save()
    #         return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': pk}))

    # context = {
    #     'formset': formset,
    # }

    obj = AtividadesTeletrabalho.objects.get(pk=pk)
    form = AtividadesTeletrabalhoForm(instance=obj)

    if request.method == 'POST':
        form = AtividadesTeletrabalhoForm(request.POST, instance=obj)
        if form.is_valid():
            obj = form.save()
            periodo_id = obj.periodo.id
            plano_trabalho_id = PeriodoTeletrabalho.objects.get(
                id=periodo_id).plano_trabalho_id
            return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': plano_trabalho_id}))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'form': form,
    }
    return render(request, 'webapp/pages/atividades-teletrabalho-form.html', context)


@login_required
def atividade_teletrabalho_delete(request, pk):
    instance = AtividadesTeletrabalho.objects.get(pk=pk)
    plano_trabalho_id = instance.periodo.plano_trabalho.id
    if instance.periodo.plano_trabalho.aprovado_chefia:
        messages.error(
            request, "Não é possível excluir uma Atividade de um Plano de Trabalho já aprovado/reprovado!")
    else:
        instance.delete()
    return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': plano_trabalho_id}))


@login_required
def atividade_cumprimento(request, pk_avaliacao, pk_atividade,  cumprimento):
    instance = AtividadesTeletrabalho.objects.get(pk=pk_atividade)
    instance.cumprimento = cumprimento
    instance.save()

    return redirect(reverse('webapp:avaliacao_atividades_list', kwargs={'pk': pk_avaliacao}))


@login_required
def autorizacoes_excecoes(request):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='GABINETE'):
        autorizacoes = AutorizacoesExcecoes.objects.all()
        context = {
            'autorizacoes': autorizacoes,
        }
        return render(request, 'webapp/pages/autorizacoes-excecoes.html', context)
    return HttpResponseBadRequest("proibido")


@login_required
def autorizacao_excecao_edit(request, pk):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='GABINETE'):
        autorizacao = AutorizacoesExcecoes.objects.get(pk=pk)

        form_instance = AutorizacoesExcecoesForm(
            instance=autorizacao)
        form = AutorizacoesExcecoesAprovaForm(instance=autorizacao)

        if request.method == 'POST':
            form = AutorizacoesExcecoesAprovaForm(
                request.POST, instance=autorizacao)

            if form.is_valid():
                form.save()
                return redirect(reverse('webapp:autorizacoes_excecoes'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

        context = {
            'form': form,
            'form_instance': form_instance,
            'declaracao': autorizacao.declaracao,
        }
        return render(request, 'webapp/pages/autorizacao-excecao-form.html', context)
    return HttpResponseBadRequest("probido-gab")


@login_required
def autorizacao_excecao_delete(request, pk):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='GABINETE'):
        autorizacao = AutorizacoesExcecoes.objects.get(pk=pk)
        autorizacao.delete()
        return redirect(reverse('webapp:autorizacoes_excecoes'))
    return HttpResponseBadRequest("proibido-gab")


@login_required
def cigt(request):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='CIGT'):
        planos_trabalho = PlanoTrabalho.objects.all()
        protocolos_autorizacao_teletrabalho = ProtocoloAutorizacaoTeletrabalho.objects.all()
        context = {
            'planos_trabalho': planos_trabalho,
            'protocolos_autorizacao_teletrabalho': protocolos_autorizacao_teletrabalho,
        }
        return render(request, 'webapp/pages/cigt.html', context)
    return HttpResponseBadRequest("proibido-cigt")


@login_required
def cigt_analisar_planos_trabalho(request):
    planos_trabalho = PlanoTrabalho.objects.all()
    context = {
        'planos_trabalho': planos_trabalho,
    }
    return render(request, 'webapp/pages/cigt-analisar-planos-trabalho.html', context)


@login_required
def cigt_analisar_protocolos_autorizacao(request):
    protocolos = ProtocoloAutorizacaoTeletrabalho.objects.all()
    context = {
        'protocolos': protocolos,
    }
    return render(request, 'webapp/pages/cigt-analisar-protocolos-autorizacao.html', context)


@login_required
def cigt_analisar_avaliacoes_mensais(request):
    avaliacoes = AvaliacaoChefia.objects.all()
    context = {
        'avaliacoes': avaliacoes,
    }
    return render(request, 'webapp/pages/cigt-analisar-avaliacoes-mensais.html', context)


@login_required
def cigt_portarias_doe(request):
    portarias = PortariasPublicadasDOE.objects.all()
    context = {
        'portarias': portarias,
    }
    return render(request, 'webapp/pages/cigt-portarias-doe.html', context)


@login_required
def cigt_portaria_doe_edit(request, pk):
    portaria = PortariasPublicadasDOE.objects.get(pk=pk)
    form = PortariaDoeEditForm(instance=portaria)
    if request.method == 'POST':
        form = PortariaDoeEditForm(request.POST, instance=portaria)
        if form.is_valid():
            form.save()
            return redirect(reverse('webapp:cigt_portarias_doe'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {'form': form}
    return render(request, 'webapp/pages/cigt-portaria-doe-form.html', context)


@login_required
def cigt_controle_mensal_teletrabalho(request):
    controle_mensal_objs = ControleMensalTeletrabalho.objects.all()
    context = {
        'controle_mensal_objs': controle_mensal_objs,
    }
    return render(request, 'webapp/pages/cigt-controle-mensal-teletrabalho.html', context)


@login_required
def avaliacoes_cigt(request):
    avaliacoes = AvaliacaoChefia.objects.all()
    context = {
        'avaliacoes': avaliacoes,
    }
    return render(request, 'webapp/pages/avaliacoes-cigt.html', context)


@login_required
def encaminhar_avaliacoes_cigt(request):
    # garante que apenas usuários do grupo CIGT
    # possam acessar a view
    if request.user.groups.filter(name='CIGT'):
        avaliacoes_encaminhadas = []
        # reescrever o método encaminha_pedido_avaliacao como um classmethod
        # que recebe como parâmetro o servidor e retorna um set com os períodos
        # em que o servidor esteve em teletrabalho.
        # retornar set para evitar mais de um encaminhamento se houver mais de um
        # plano de trabalho no mesmo período.

        # verificar se isso é problema:
        # pensar sobre como fazer o controle para não enviar pedidos para servidores
        # que não fizeram teletrabalho porque o plano foi alterado e também
        # para servidores que não estão mais com o período vigente mas fizeram o
        # teletrabalho em período pretérito. ideia: definir um campo de data para
        # registrar se o servidor saiu do teletrabalho
        for protocolo_autorizacao in ProtocoloAutorizacaoTeletrabalho.objects.all():
            for avaliacao in protocolo_autorizacao.encaminha_pedido_avaliacao():
                avaliacoes_encaminhadas.append(avaliacao)
        context = {
            'avaliacoes_encaminhadas': avaliacoes_encaminhadas,
        }
        return redirect(reverse('webapp:cigt_analisar_avaliacoes_mensais'))
    return HttpResponseBadRequest("proibido-cigt")


@login_required
def verificar_retorno_avaliacoes_cigt(request):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='CIGT'):
        avaliacoes_pendentes = []
        for protocolo_autorizacao in ProtocoloAutorizacaoTeletrabalho.objects.all():
            for avaliacao in protocolo_autorizacao.verifica_avaliacoes():
                avaliacoes_pendentes.append(avaliacao)
        context = {
            'avaliacoes_pendentes': avaliacoes_pendentes,
        }
        return render(request, 'webapp/pages/verificar-retorno-avaliacoes-cigt.html', context)
    return HttpResponseBadRequest("proibido-cigt")


# @login_required
# def encaminhar_verificar_avaliacoes_cigt(request):
#     if request.user.groups.filter(name='CIGT'):
#         avaliacoes_pendentes = []
#         for protocolo_autorizacao in ProtocoloAutorizacaoTeletrabalho.objects.all():
#             for avaliacao in protocolo_autorizacao.verifica_avaliacoes():
#                 avaliacoes_pendentes.append(avaliacao)
#         context = {
#             'avaliacoes_pendentes': avaliacoes_pendentes,
#         }
#         return render(request, 'webapp/pages/verificar-retorno-avaliacoes-cigt.html', context)
#     return HttpResponseBadRequest("proibido-cigt")


@login_required
def protocolos_autorizacao_teletrabalho(request):
    protocolos = ProtocoloAutorizacaoTeletrabalho.objects.filter(
        despacho_cigt__plano_trabalho__manifestacao__servidor=request.user
    )
    context = {
        'protocolos': protocolos,
    }
    return render(request, 'webapp/pages/protocolos-autorizacao-teletrabalho.html', context)


@login_required
def protocolo_autorizacao_teletrabalho_edit(request, pk):
    protocolo_autorizacao = ProtocoloAutorizacaoTeletrabalho.objects.get(pk=pk)
    form_instance = ProtocoloAutorizacaoTeletrabalhoAprovaForm(
        instance=protocolo_autorizacao)
    form = ProtocoloAutorizacaoTeletrabalhoForm(
        instance=protocolo_autorizacao)
    if request.method == 'POST':
        form = ProtocoloAutorizacaoTeletrabalhoForm(
            request.POST, instance=protocolo_autorizacao)
        if form.is_valid():
            form.save()
            return redirect(reverse('webapp:cigt_analisar_protocolos_autorizacao'))

        for _, error_list in form.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'form': form,
        'form_instance': form_instance,
    }
    return render(request, 'webapp/pages/protocolo-autorizacao-teletrabalho-form.html', context)


@login_required
def servidor(request):
    # checar o cadastro
    servidor = Servidor.objects.get(user=request.user)
    check_dados = servidor.check_dados()
    # verifica se existe Manifestacao de Interesse
    last_manifestacao_interesse = ManifestacaoInteresse.objects.filter(
        lotacao__servidor__user=request.user).last()
    # verifica se a Manifestação já foi aprovada pela chefia
    # verifica se existe Declaração de Não Enquadramento
    last_declaracao_nao_enquadramento = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        manifestacao__lotacao__servidor__user=request.user)
    last_plano_trabalho = PlanoTrabalho.objects.filter(
        manifestacao__lotacao__servidor__user=request.user)
    # verifica se existe pendencia de autorização para teletrabalho das chefias
    autorizacoes_excecao_chefia = AutorizacoesExcecoes.objects.filter(
        declaracao__manifestacao__lotacao__servidor__user=request.user)

    context = {
        'check_dados': check_dados,
        'last_manifestacao_interesse': last_manifestacao_interesse,
        'last_declaracao_nao_enquadramento': last_declaracao_nao_enquadramento,
        'last_plano_trabalho': last_plano_trabalho,
        'autorizacoes_excecao_chefia': autorizacoes_excecao_chefia,
    }

    return render(request, 'webapp/pages/servidor.html', context)


@login_required
def chefia_imediata(request):
    if request.user.groups.filter(name='CHEFIAS'):
        manifestacoes_servidor = ManifestacaoInteresse.objects.filter(
            servidor=request.user)
        manifestacoes_subordinados = ManifestacaoInteresse.objects.filter(
            chefia_imediata=request.user)
        planos_trabalho_subordinados = PlanoTrabalho.objects.filter(
            manifestacao__chefia_imediata=request.user)
        context = {

            'manifestacoes_servidor': manifestacoes_servidor,
            'manifestacoes_subordinados': manifestacoes_subordinados,
            'planos_trabalho_subordinados': planos_trabalho_subordinados,
        }
        return render(request, 'webapp/pages/chefia-imediata.html', context)
    return HttpResponseBadRequest("proibido-chefia-imediata")


@login_required
def chefia_imediata_analisar_manifestacoes(request):
    manifestacoes_subordinados = ManifestacaoInteresse.objects.filter(
        chefia_imediata=request.user)
    context = {
        'manifestacoes_subordinados': manifestacoes_subordinados,
    }
    return render(request, 'webapp/pages/chefia-imediata-analisar-manifestacoes.html', context)


@login_required
def chefia_imediata_analisar_planos_trabalho(request):
    planos_trabalho = PlanoTrabalho.objects.filter(
        manifestacao__chefia_imediata=request.user)
    context = {
        'planos_trabalho': planos_trabalho,
    }
    return render(request, 'webapp/pages/chefia-imediata-analisar-planos-trabalho.html', context)


@login_required
def chefia_imediata_realizar_avaliacoes_mensais(request):
    if request.user.groups.filter(name='CHEFIAS'):
        pareceres_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        context = {
            'avaliacoes_chefia': avaliacoes_chefia,
        }
        return render(request, 'webapp/pages/chefia-imediata-avaliacoes-mensais.html', context)
    return HttpResponseBadRequest("proibido-chefia-imediata")


@login_required
def avaliacoes_chefia(request):
    if request.user.groups.filter(name='CHEFIAS'):
        pareceres_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        context = {
            'avaliacoes_chefia': avaliacoes_chefia,
        }
        return render(request, 'webapp/pages/avaliacoes-chefia.html', context)
    return HttpResponseBadRequest("proibido-chefia-imediata")


@login_required
def avaliacao_atividades_list(request, pk):
    # garante que apenas usuários com grupo CHEFIAS
    # possam fazer a avaliação
    if request.user.groups.filter(name='CHEFIAS') or request.user.groups.filter(name='CIGT'):
        avaliacao = AvaliacaoChefia.objects.get(pk=pk)
        pareceres_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        # garante que apenas a chefia imediata apontada na manifestação de
        # interesse possa fazer a avalicação
        if not avaliacoes_chefia.filter(pk=pk) and not request.user.groups.filter(name='CIGT'):
            return HttpResponseBadRequest('proibido-avaliacao-chefia')

        plano_trabalho = avaliacao.get_plano_trabalho()
        periodo_para_avaliacao = avaliacao.get_periodo_para_avaliacao()

        # problema -> periodo_para_avaliacao
        # resolver: se o periodo for maior que um um mês, o filtro não vai retornar nada
        # exemplo: periodo 1/1/2024 a 1/5/2024
        # porque o período de avaliacao é sempre mensal
        # pensar como resolver isso
        #

        # talvez para garantir as avaliações mensais devemos criar apenas períodos mensais
        # se o usuário colocar um período maior que um mês, dividimos em meses e gravamos
        # tudo para controlar por mês posteriormente.

        ### SOLUÇÃO ###
        # é só fazer uma validação para o usuário não conseguir colocar mais de um mês no form
        # para cada entrada

        periodos_para_avaliacao = avaliacao.get_periodos_para_avaliacao()
        atividades_para_avaliacao = avaliacao.get_atividades_para_avaliacao()

        form = AvaliacaoChefiaFinalizaForm(instance=avaliacao)

        forms_cumprimento = [AtividadeCumprimentoForm(instance=atividade)
                             for atividade in atividades_para_avaliacao]

        atividades_e_forms = zip(atividades_para_avaliacao, forms_cumprimento)

        if request.user.groups.filter(name='CHEFIAS'):
            if request.method == 'POST':
                form = AvaliacaoChefiaFinalizaForm(
                    request.POST, instance=avaliacao)

                if form.is_valid():
                    for atividade, cumprimento in zip(atividades_para_avaliacao, request.POST.getlist('cumprimento')):
                        atividade.cumprimento = cumprimento
                        atividade.save()
                    form.save()
                    return redirect(reverse('webapp:chefia_imediata_realizar_avaliacoes_mensais'))

        context = {
            'plano_trabalho': plano_trabalho,
            'periodo_para_avaliacao': periodo_para_avaliacao,
            'periodos_para_avaliacao': periodos_para_avaliacao,
            'atividades_para_avaliacao': atividades_para_avaliacao,
            'avaliacao': avaliacao,
            'pk_avaliacao': pk,
            'form': form,
            'atividades_e_forms': atividades_e_forms,
            'user_chefia': request.user.groups.filter(name='CHEFIAS'),
        }

        return render(request, 'webapp/pages/avaliacao-chefia-atividades-list.html', context)


@login_required
def finalizar_avaliacao(request, pk):
    # Criar uma função que verifique se a avaliação já foi finalizada.
    # Caso já tenha sido finalizada, criar um log em uma tabela espefícica
    # para salvar o estado anterior. Nessa tabela de Log, criar um campo
    # para justificativa da alteração da avaliacação.

    form = AvaliacaoChefiaFinalizaForm()

    if request.method == 'POST':
        form = AvaliacaoChefiaFinalizaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('webapp:avaliacoes_chefia'))

    # avaliacao = AvaliacaoChefia.objects.get(pk=pk)
    # avaliacao.finalizar_avaliacao = True
    # avaliacao.save()


@login_required
def avaliacao_chefia_atividade(request, pk):
    periodo = PeriodoTeletrabalho.objects.get(pk=pk)
    AtividadesTeletrabalhoFormSet = inlineformset_factory(
        PeriodoTeletrabalho, AtividadesTeletrabalho, fields=(
            "periodo", "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa", "cumprimento", "justificativa_nao_cumprimento"),
        extra=0, min_num=1)
    formset = AtividadesTeletrabalhoFormSet(
        instance=periodo)

    if request.method == 'POST':
        formset = AtividadesTeletrabalhoFormSet(request.POST, instance=periodo)
        if formset.is_valid():
            formset.save()
            # verificar o cumprimento total, parcial ou descumprimento
            return redirect(reverse('webapp:avaliacoes_chefia'))

        for _, error_list in formset.errors.items():
            for e in error_list:
                messages.error(request, e)

    context = {
        'formset': formset
    }
    return render(request, 'webapp/pages/avaliacao-chefia-atividade-form.html', context)


@login_required
def avaliacao_chefia_edit(request, pk):
    # garante que apenas usuários com grupo CHEFIAS
    # possam fazer a avaliação
    if request.user.groups.filter(name='CHEFIAS'):
        avaliacao = AvaliacaoChefia.objects.get(pk=pk)
        pareceres_cigt = DespachoCIGTPlanoTrabalho.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        # garante que apenas a chefia imediata apontada na manifestação de
        # interesse possa fazer a avalicação
        if not avaliacoes_chefia.filter(pk=pk):
            return HttpResponseBadRequest('proibido-avaliacao-chefia')

        atividades_para_avaliacao = avaliacao.get_atividades_para_avaliacao()

        AtividadesTeletrabalhoFormSet = inlineformset_factory(
            PeriodoTeletrabalho, AtividadesTeletrabalho, fields=(
                "periodo", "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa", "cumprimento", "justificativa_nao_cumprimento"),
            extra=0, min_num=1)
        formset = AtividadesTeletrabalhoFormSet(
            instance=atividades_para_avaliacao.first().periodo)

        form = AvaliacaoChefiaForm(instance=avaliacao)
        if request.method == 'POST':
            form = AvaliacaoChefiaForm(request.POST, instance=avaliacao)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.modificado_por = request.user
                obj.save()
                return redirect(reverse('webapp:avaliacoes_chefia'))

            for _, error_list in form.errors.items():
                for e in error_list:
                    messages.error(request, e)

        context = {
            'atividades_para_avaliacao': atividades_para_avaliacao,
            'avaliacao': avaliacao,
            'form': form,
            'formset': formset,
        }
        return render(request, 'webapp/pages/avaliacao-chefia-form.html', context)

    return HttpResponseBadRequest("proibido-chefia-imediata")


@login_required
def gabinete(request):
    if request.user.groups.filter(name='GABINETE'):
        context = {}
        return render(request, 'webapp/pages/gabinete.html', context)
    return HttpResponseBadRequest("proibido-gabinete")


@login_required
def gerar_portaria_doe(request):
    if request.user.groups.filter(name='CIGT'):
        obj = ProtocoloAutorizacaoTeletrabalho.generate_portaria_publicacao()
        if not obj:
            # posteriormente separara as duas situações: em que falta o sid e em que não há modificação para publicar
            return HttpResponseBadRequest("VERIFIQUE TODOS OS SIDS NOS PROTOCOLOS DE AUTORIZACAO | NÃO HÁ NENHUMA MODIFICAÇÃO")
        obj.render_docx_tpl(tipo_doc='portaria_teletrabalho_doe')
        try:
            if os.path.exists(obj.docx.path):
                with open(obj.docx.path, 'rb') as fh:
                    # response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
                    # response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo("portaria_teletrabalho_doe")}'  # noqa E501
                    # return response
                    return redirect(reverse('webapp:cigt_portarias_doe'))
        except ValueError:
            raise Exception('error generating docx file: associated docx not generated')  # noqa E501
        except AttributeError:
            return HttpResponseBadRequest("Ainda não foi gerada nenhuma Portaria!")
        return redirect('webapp:cigt')
    return HttpResponseBadRequest("proibido-cigt")


@login_required
def download_portaria_doe(request, pk):
    if request.user.groups.filter(name='CIGT'):
        obj = PortariasPublicadasDOE.objects.get(pk=pk)
        # obj.render_docx_tpl(tipo_doc='docx', save_input=False)
        # path_file_temp = obj.get_path_file_temp(tipo_doc='docx')
        try:
            if os.path.exists(obj.docx.path):
                context = {
                    'diretor_em_exercicio': obj.diretor_em_exercicio,
                }
                obj.render_docx_custom_tpl(
                    tipo_doc='docx', path_tpl=obj.docx.path, context=context)
                with open(obj.get_path_file_temp(tipo_doc='docx'), 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
                    response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo("portaria_teletrabalho_doe")}'  # noqa E501
                    return response
        except ValueError:
            raise Exception('error generating docx file: associated docx not generated')  # noqa E501
        except AttributeError:
            return HttpResponseBadRequest("Ainda não foi gerada nenhuma Portaria!")
        return redirect('webapp:cigt')
    return HttpResponseBadRequest("proibido-cigt")


@login_required
def download_docx(request, model, pk):
    if True:  # request.user.groups.filter(name='CIGT'):
        if model == 'portaria':
            obj = PortariasPublicadasDOE.objects.get(pk=pk)
            nome_arquivo = 'portaria_teletrabalho_doe'
        elif model == 'manifestacao':
            obj = ManifestacaoInteresse.objects.get(pk=pk)
            nome_arquivo = 'manifestacao_interesse'
        elif model == 'declaracao':
            obj = DeclaracaoNaoEnquadramentoVedacoes.objects.get(pk=pk)
            nome_arquivo = 'declaracao_nao_enquadramento_vedacoes'
        elif model == 'plano-trabalho':
            obj = PlanoTrabalho.objects.get(pk=pk)
            nome_arquivo = 'plano_trabalho'
        elif model == 'autorizacao-excecao':
            obj = AutorizacoesExcecoes.objects.get(pk=pk)
            nome_arquivo = 'autorizacao_excecoes_chefias'
        elif model == 'avaliacao':
            obj = AvaliacaoChefia.objects.get(pk=pk)
            nome_arquivo = 'avaliacao_chefia'
        elif model == 'protocolo-autorizacao':
            obj = ProtocoloAutorizacaoTeletrabalho.objects.get(pk=pk)
            nome_arquivo = 'protocolo_autorizacao'
        elif model == 'despacho-cigt-plano-trabalho':
            obj = DespachoCIGTPlanoTrabalho.objects.get(pk=pk)
            nome_arquivo = 'despacho_cigt_plano_trabalho'
        else:
            return HttpResponseBadRequest("tipo-incorreto-arquivo")
        try:
            if os.path.exists(obj.docx.path):
                ...
        except ValueError:
            obj.render_docx_tpl(tipo_doc=nome_arquivo)

        with open(obj.docx.path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
            response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo(nome_arquivo)}'  # noqa E501
            return response

    return HttpResponseBadRequest("proibido-cigt")


@login_required
def htmx_adiciona_periodo(request):
    form = PeriodoTeletrabalhoForm()
    context = {
        'form': form,
    }
    return render(request, 'webapp/partials/add_periodo.html', context)


@login_required
def htmx_adiciona_atividade(request):
    form = AtividadesTeletrabalhoForm()
    context = {
        'form': form,
    }
    return render(request, 'webapp/partials/add_atividade.html', context)
