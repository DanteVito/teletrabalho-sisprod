import os
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse

from authentication.models import User
from render.forms import (AtividadesTeletrabalhoForm, AutorizacoesExcecoesForm,
                          AvaliacaoChefiaForm,
                          DeclaracaoNaoEnquadramentoVedacoesForm,
                          ManifestacaoInteresseAprovadoChefiaForm,
                          ManifestacaoInteresseForm, PeriodoTeletrabalhoForm,
                          PlanoTrabalhoForm,
                          PlanoTrabalhoFormAprovadoChefiaForm,
                          PlanoTrabalhoFormAprovadoCIGTForm,
                          ProtocoloAutorizacaoTeletrabalhoForm, UserForm)
from render.models import (AtividadesTeletrabalho, AutorizacoesExcecoes,
                           AvaliacaoChefia, DeclaracaoNaoEnquadramentoVedacoes,
                           ListaPostosTrabalho, ManifestacaoInteresse,
                           ModeloDocumento, ParecerCIGT, PeriodoTeletrabalho,
                           PlanoTrabalho, PortariasPublicadasDOE,
                           ProtocoloAutorizacaoTeletrabalho, Setor, Unidade)


@login_required
def home(request):
    context = {
    }
    return render(request, 'webapp/pages/home.html', context)


@login_required
def dados_cadastrais(request):
    user_groups = request.user.groups.all()

    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
        return redirect(reverse('webapp:servidor'))

    context = {
        'form': form,
        'user_groups': user_groups,
    }

    return render(request, 'webapp/pages/dados-cadastrais.html', context)


@login_required
def manifestacao_interesse(request):
    manifestacoes_servidor = ManifestacaoInteresse.objects.filter(
        servidor=request.user)

    context = {
        'manifestacoes_servidor': manifestacoes_servidor,
    }
    return render(request, 'webapp/pages/manifestacao-interesse.html', context)


@login_required
def manifestacao_interesse_create(request):
    form = ManifestacaoInteresseForm()
    if request.method == 'POST':
        form = ManifestacaoInteresseForm(request.POST)
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

    form = ManifestacaoInteresseForm(instance=instance)
    if request.method == 'POST':
        form = ManifestacaoInteresseForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.servidor = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='MANIFESTACAO INTERESSE')
            obj.save()
            messages.info(request, "Manifestação alterada com sucesso!")
            return redirect(reverse('webapp:manifestacao_interesse'))
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

    form_instance = ManifestacaoInteresseForm(instance=manifestacao)
    form = ManifestacaoInteresseAprovadoChefiaForm(instance=manifestacao)
    if request.method == 'POST':
        form = ManifestacaoInteresseAprovadoChefiaForm(
            request.POST, instance=manifestacao)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()
            return redirect(reverse('webapp:chefia_imediata'))
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
    declaracaoes = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        manifestacao__servidor=request.user)

    context = {
        'declaracoes': declaracaoes
    }
    return render(request, 'webapp/pages/declaracao-nao-enquadramento.html', context)


@login_required
def declaracao_nao_enquadramento_create(request):
    form = DeclaracaoNaoEnquadramentoVedacoesForm()
    if request.method == 'POST':
        form = DeclaracaoNaoEnquadramentoVedacoesForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.adicionado_por = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='DECLARACAO NAO ENQUADRAMENTO VEDACOES')
            obj.save()
            messages.info(request, "Declaração cadastrada com sucesso!")
            return redirect(reverse('webapp:declaracao_nao_enquadramento'))

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

    form = DeclaracaoNaoEnquadramentoVedacoesForm(instance=instance)
    if request.method == 'POST':
        form = DeclaracaoNaoEnquadramentoVedacoesForm(
            request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()
            messages.info(request, "Declaração alterada com sucesso!")
            return redirect(reverse('webapp:declaracao_nao_enquadramento'))

    context = {
        'tipo_form': 'edit',
        'form': form
    }
    return render(request, 'webapp/pages/declaracao-nao-enquadramento-form.html', context)


@login_required
def declaracao_nao_enquadramento_delete(request, pk):
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
    planos_trabalho = PlanoTrabalho.objects.filter(
        manifestacao__servidor=request.user)
    context = {
        'planos_trabalho': planos_trabalho
    }
    return render(request, 'webapp/pages/plano-trabalho.html', context)


@login_required
def plano_trabalho_create(request):
    form = PlanoTrabalhoForm()
    PeriodoTeletrabalhoFormSet = inlineformset_factory(
        PlanoTrabalho, PeriodoTeletrabalho, fields=("data_inicio", "data_fim")
    )
    periodos_formset = PeriodoTeletrabalhoFormSet()
    AtividadesTeletrabalhoFormSet = inlineformset_factory(
        PlanoTrabalho, AtividadesTeletrabalho, fields=(
            "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa")
    )
    atividades_formset = AtividadesTeletrabalhoFormSet()
    if request.method == 'POST':
        form = PlanoTrabalhoForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.adicionado_por = request.user
            obj.modificado_por = request.user
            obj.modelo = ModeloDocumento.objects.get(
                nome_modelo='PLANO DE TRABALHO')
            obj.save()

            # when using commit=False we must call save_m2m()
            # for many to many fields

            form.save_m2m()

            periodos_formset = PeriodoTeletrabalhoFormSet(
                request.POST, instance=obj)
            if periodos_formset.is_valid():
                periodos_formset.save()

            atividades_formset = AtividadesTeletrabalhoFormSet(
                request.POST, instance=obj)
            if atividades_formset.is_valid():
                atividades_formset.save()
            messages.info(request, "Plano de Trabalho cadastrado com sucesso!")
            return redirect(reverse('webapp:plano_trabalho'))

    context = {
        'tipo_form': 'create',
        'form': form,
        'periodos_formset': periodos_formset,
        'atividades_formset': atividades_formset,
    }
    return render(request, 'webapp/pages/plano-trabalho-form.html', context)


@login_required
def plano_trabalho_edit(request, pk):
    try:
        instance = PlanoTrabalho.objects.get(
            pk=pk)
    except PlanoTrabalho.DoesNotExist:
        return HttpResponseBadRequest()

    periodos_teletrabalho = PeriodoTeletrabalho.objects.filter(
        plano_trabalho=instance)
    form = PlanoTrabalhoForm(instance=instance)
    if request.method == 'POST':
        form = PlanoTrabalhoForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()

            # when using commit=False we must call save_m2m()
            # for many to many fields

            form.save_m2m()

            messages.info(request, "Plano de Trabalho alterado com sucesso!")
            return redirect(reverse('webapp:plano_trabalho'))
    context = {
        'tipo_form': 'edit',
        'periodos_teletrabalho': periodos_teletrabalho,
        'form': form,
        'periodos_teletrabalho': PeriodoTeletrabalho.objects.filter(plano_trabalho=instance),
        'atividades_teletrabalho': AtividadesTeletrabalho.objects.filter(plano_trabalho=instance)
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

    form_instance = PlanoTrabalhoForm(instance=plano_trabalho)
    form = PlanoTrabalhoFormAprovadoChefiaForm(instance=plano_trabalho)
    if request.method == 'POST':
        form = PlanoTrabalhoFormAprovadoChefiaForm(
            request.POST, instance=plano_trabalho)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.modificado_por = request.user
            obj.save()
            return redirect(reverse('webapp:chefia_imediata'))
    context = {
        'plano_trabalho': plano_trabalho,
        'form': form,
        'form_instance': form_instance,
    }
    return render(request, 'webapp/pages/plano-trabalho-aprovado-chefia.html', context)


@login_required
def plano_trabalho_aprovado_cigt(request, pk):
    # garante que apenas o usuário registrado como do grupo CIGT
    # possa aprovar o plano de trabalho
    if request.user.groups.filter(name="CIGT"):
        plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
        form_instance = PlanoTrabalhoForm(instance=plano_trabalho)
        form = PlanoTrabalhoFormAprovadoCIGTForm(instance=plano_trabalho)
        if request.method == 'POST':
            form = PlanoTrabalhoFormAprovadoCIGTForm(
                request.POST, instance=plano_trabalho)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.modificado_por = request.user
                obj.usuario_cigt_aprovacao = request.user
                obj.save()
                return redirect(reverse('webapp:cigt'))
        context = {
            'plano_trabalho': plano_trabalho,
            'form': form,
            'form_instance': form_instance,
        }
        return render(request, 'webapp/pages/plano-trabalho-aprovado-cigt.html', context)
    return HttpResponseBadRequest("proibido")


@login_required
def plano_trabalho_delete(request, pk):
    planos_trabalho = PlanoTrabalho.objects.all()

    context = {
        'planos_trabalho': planos_trabalho
    }
    return render(request, 'webapp/pages/plano-trabalho.html', context)


@login_required
def periodo_teletrabalho(request, pk):
    # note que pk é a chave primária do plano de trabalho
    PeriodoTeletrabalhoFormSet = inlineformset_factory(
        PlanoTrabalho, PeriodoTeletrabalho, fields=("data_inicio", "data_fim")
    )
    plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    formset = PeriodoTeletrabalhoFormSet(instance=plano_trabalho)
    if request.method == 'POST':
        formset = PeriodoTeletrabalhoFormSet(
            request.POST, instance=plano_trabalho)
        if formset.is_valid():
            formset.save()
            plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
            # formset = PeriodoTeletrabalhoFormSet(instance=plano_trabalho)
            return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': pk}))
    context = {
        'formset': formset,
    }
    return render(request, 'webapp/pages/periodo-teletrabalho-form.html', context)


@login_required
def periodo_teletrabalho_delete(request, pk):
    instance = PeriodoTeletrabalho.objects.get(pk=pk)
    instance.delete()
    return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': instance.plano_trabalho_id}))


@login_required
def atividade_teletrabalho(request, pk):
    # note que pk é a chave primária do plano de trabalho
    AtividadesTeletrabalhoFormSet = inlineformset_factory(
        PlanoTrabalho, AtividadesTeletrabalho, fields=(
            "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa")
    )
    plano_trabalho = PlanoTrabalho.objects.get(pk=pk)
    formset = AtividadesTeletrabalhoFormSet(instance=plano_trabalho)
    if request.method == 'POST':
        formset = AtividadesTeletrabalhoFormSet(
            request.POST, instance=plano_trabalho)
        if formset.is_valid():
            formset.save()
            return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': pk}))

    context = {
        'formset': formset,
    }
    return render(request, 'webapp/pages/atividades-teletrabalho-form.html', context)


@login_required
def atividade_teletrabalho_delete(request, pk):
    instance = AtividadesTeletrabalho.objects.get(pk=pk)
    instance.delete()
    return redirect(reverse('webapp:plano_trabalho_edit', kwargs={'pk': instance.plano_trabalho_id}))


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
        form = AutorizacoesExcecoesForm(instance=autorizacao)
        if request.method == 'POST':
            form = AutorizacoesExcecoesForm(request.POST, instance=autorizacao)
            if form.is_valid():
                form.save()
                return redirect(reverse('webapp:autorizacoes_excecoes'))
        context = {
            'form': form,
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
def encaminhar_avaliacoes_cigt(request):
    # garante que apenas usuários do grupo GABINETE
    # possam acessar a view
    if request.user.groups.filter(name='CIGT'):
        avaliacoes_encaminhadas = []
        for protocolo_autorizacao in ProtocoloAutorizacaoTeletrabalho.objects.all():
            for avaliacao in protocolo_autorizacao.encaminha_pedido_avaliacao():
                avaliacoes_encaminhadas.append(avaliacao)
        context = {
            'avaliacoes_encaminhadas': avaliacoes_encaminhadas,
        }
        return render(request, 'webapp/pages/encaminhar-avaliacoes-cigt.html', context)
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
    form = ProtocoloAutorizacaoTeletrabalhoForm(instance=protocolo_autorizacao)
    if request.method == 'POST':
        form = ProtocoloAutorizacaoTeletrabalhoForm(
            request.POST, instance=protocolo_autorizacao)
        if form.is_valid():
            form.save()
            return redirect(reverse('webapp:protocolos_autorizacao_teletrabalho'))
    context = {
        'form': form,
    }
    return render(request, 'webapp/pages/protocolo-autorizacao-teletrabalho-form.html', context)


@login_required
def servidor(request):
    # checar o cadastro
    check_cadastro = request.user.check_dados()
    # verifica se existe Manifestacao de Interesse
    last_manifestacao_interesse = ManifestacaoInteresse.objects.filter(
        servidor=request.user).last()
    # verifica se a Manifestação já foi aprovada pela chefia
    # verifica se existe Declaração de Não Enquadramento
    last_declaracao_nao_enquadramento = DeclaracaoNaoEnquadramentoVedacoes.objects.filter(
        manifestacao__servidor=request.user)
    last_plano_trabalho = PlanoTrabalho.objects.filter(
        manifestacao__servidor=request.user)

    context = {
        'check_cadastro': check_cadastro,
        'last_manifestacao_interesse': last_manifestacao_interesse,
        'last_declaracao_nao_enquadramento': last_declaracao_nao_enquadramento,
        'last_plano_trabalho': last_plano_trabalho,
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
def avaliacoes_chefia(request):
    if request.user.groups.filter(name='CHEFIAS'):
        pareceres_cigt = ParecerCIGT.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        context = {
            'avaliacoes_chefia': avaliacoes_chefia,
        }
        return render(request, 'webapp/pages/avaliacoes-chefia.html', context)
    return HttpResponseBadRequest("proibido-chefia-imediata")


@login_required
def avaliacao_chefia_edit(request, pk):
    # garante que apenas usuários com grupo CHEFIAS
    # possam fazer a avaliação
    if request.user.groups.filter(name='CHEFIAS'):
        avaliacao = AvaliacaoChefia.objects.get(pk=pk)
        pareceres_cigt = ParecerCIGT.objects.filter(
            plano_trabalho__manifestacao__chefia_imediata=request.user)
        avaliacoes_chefia = AvaliacaoChefia.objects.filter(
            encaminhamento_avaliacao_cigt__despacho_cigt__in=pareceres_cigt)
        # garante que apenas a chefia imediata apontada na manifestação de
        # interesse possa fazer a avalicação
        if not avaliacoes_chefia.filter(pk=pk):
            return HttpResponseBadRequest('proibido-avaliacao-chefia')

        form = AvaliacaoChefiaForm(instance=avaliacao)
        if request.method == 'POST':
            form = AvaliacaoChefiaForm(request.POST, instance=avaliacao)
            if form.is_valid():
                obj = form.save(commit=False)
                obj.modificado_por = request.user
                obj.save()
                return redirect(reverse('webapp:avaliacoes_chefia'))
        context = {
            'avaliacao': avaliacao,
            'form': form
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
def gerar_portaria_doe(request, commit_doe):
    if request.user.groups.filter(name='CIGT'):
        if commit_doe:
            obj = ProtocoloAutorizacaoTeletrabalho.generate_portaria_publicacao()
            if not obj:
                return HttpResponseBadRequest("VERIFIQUE TODOS OS SIDS NOS PROTOCOLOS DE AUTORIZACAO")
            obj.render_docx_tpl('portaria_repr')
        else:
            obj = PortariasPublicadasDOE.objects.last()
        try:
            if os.path.exists(obj.docx.path):
                with open(obj.docx.path, 'rb') as fh:
                    response = HttpResponse(fh.read(), content_type='application/docx')  # noqa E501
                    response['Content-Disposition'] = f'filename={obj.gerar_nome_arquivo("portaria_repr")}_{date.today()}.docx'  # noqa E501
                    return response
        except ValueError:
            raise Exception('error generating docx file: associated docx not generated')  # noqa E501
        except AttributeError:
            return HttpResponseBadRequest("Ainda não foi gerada nenhuma Portaria!")
        return redirect('webapp:cigt')
    return HttpResponseBadRequest("proibido-cigt")
