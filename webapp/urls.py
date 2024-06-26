from django.urls import path

from . import views

app_name = "webapp"

urlpatterns = [
    path("", views.home, name="home"),
    # dados-cadastrais
    path("dados-cadastrais/", views.dados_cadastrais, name="dados_cadastrais"),
    # manifestacao-interesse
    path(
        "manifestacao-interesse/",
        views.manifestacao_interesse,
        name="manifestacao_interesse",
    ),
    path(
        "manifestacao-interesse/create",
        views.manifestacao_interesse_create,
        name="manifestacao_interesse_create",
    ),
    path(
        "manifestacao-interesse/chefia/<int:pk>/",
        views.manifestacao_interesse_aprovado_chefia,
        name="manifestacao_interesse_aprovado_chefia",
    ),
    path(
        "manifestacao-interesse/delete/<int:pk>/",
        views.manifestacao_interesse_delete,
        name="manifestacao_interesse_delete",
    ),
    # declaracao-nao-enquadramento-nas-vedacoes
    path(
        "declaracao-nao-enquadramento/",
        views.declaracao_nao_enquadramento,
        name="declaracao_nao_enquadramento",
    ),
    path(
        "declaracao-nao-enquadramento-create/",
        views.declaracao_nao_enquadramento_create,
        name="declaracao_nao_enquadramento_create",
    ),
    # plano-de-trabalho
    path("plano-trabalho/", views.plano_trabalho, name="plano_trabalho"),
    path(
        "plano-trabalho/create/",
        views.plano_trabalho_create,
        name="plano_trabalho_create",
    ),
    path(
        "plano-trabalho/edit/<int:pk>",
        views.plano_trabalho_edit,
        name="plano_trabalho_edit",
    ),
    path(
        "plano-trabalho/chefia/<int:pk>/",
        views.plano_trabalho_aprovado_chefia,
        name="plano_trabalho_aprovado_chefia",
    ),
    path(
        "plano-trabalho/cigt/<int:pk>/",
        views.plano_trabalho_aprovado_cigt,
        name="plano_trabalho_aprovado_cigt",
    ),
    path(
        "plano-trabalho/delete/<int:pk>",
        views.plano_trabalho_delete,
        name="plano_trabalho_delete",
    ),
    # periodo teletrabalho
    path(
        "periodo-teletrabalho/<int:pk>",
        views.periodo_teletrabalho,
        name="periodo_teletrabalho",
    ),
    path(
        "periodo-teletrabalho/delete/<int:pk>",
        views.periodo_teletrabalho_delete,
        name="periodo_teletrabalho_delete",
    ),
    # atividades teletrabalho
    path(
        "atividade-teletrabalho/<int:pk>",
        views.atividade_teletrabalho,
        name="atividade_teletrabalho",
    ),
    path(
        "atividade-teletrabalho/delete/<int:pk>",
        views.atividade_teletrabalho_delete,
        name="atividade_teletrabalho_delete",
    ),
    path(
        "atividade-cumprimento/<int:pk_avaliacao>/<int:pk_atividade>/<str:cumprimento>",
        views.atividade_cumprimento,
        name="atividade_cumprimento",
    ),
    # autorizacoes excecoes chefias
    path(
        "autorizacoes-excecoes/",
        views.autorizacoes_excecoes,
        name="autorizacoes_excecoes",
    ),
    path(
        "autorizacao-excecao/edit/<int:pk>",
        views.autorizacao_excecao_edit,
        name="autorizacao_excecao_edit",
    ),
    path(
        "autorizacao-excecao/delete/<int:pk>",
        views.autorizacao_excecao_delete,
        name="autorizacao_excecao_delete",
    ),
    # cigt
    path("cigt/", views.cigt, name="cigt"),
    path(
        "cigt/analisar-planos-trabalho",
        views.cigt_analisar_planos_trabalho,
        name="cigt_analisar_planos_trabalho",
    ),
    path(
        "cigt/analisar-protocolos-autorizacao",
        views.cigt_analisar_protocolos_autorizacao,
        name="cigt_analisar_protocolos_autorizacao",
    ),
    path(
        "cigt/analisar-avaliacoes-mensais",
        views.cigt_analisar_avaliacoes_mensais,
        name="cigt_analisar_avaliacoes_mensais",
    ),
    path(
        "cigt/controle-mensal-teletrabalho",
        views.cigt_controle_mensal_teletrabalho,
        name="cigt_controle_mensal_teletrabalho",
    ),
    path("cigt/portarias-doe", views.cigt_portarias_doe, name="cigt_portarias_doe"),
    path(
        "cigt/portarias-doe/<int:pk>",
        views.cigt_portaria_doe_edit,
        name="cigt_portaria_doe_edit",
    ),
    path(
        "cigt/download-portarias-doe/<int:pk>",
        views.download_portaria_doe,
        name="download_portaria_doe",
    ),
    path("avaliacoes-cigt/", views.avaliacoes_cigt, name="avaliacoes_cigt"),
    path(
        "encaminhar-avaliacoes-cigt/",
        views.encaminhar_avaliacoes_cigt,
        name="encaminhar_avaliacoes_cigt",
    ),
    path(
        "verificar-retorno-avaliacoes-cigt/",
        views.verificar_retorno_avaliacoes_cigt,
        name="verificar_retorno_avaliacoes_cigt",
    ),
    path("gerar_portaria_doe/", views.gerar_portaria_doe, name="gerar_portaria_doe"),
    # protocolos autotorizacao teletrabalho
    path(
        "protocolos-autorizacao-teletrabalho/",
        views.protocolos_autorizacao_teletrabalho,
        name="protocolos_autorizacao_teletrabalho",
    ),
    path(
        "protocolo-autorizacao-teletrabalho/edit/<int:pk>",
        views.protocolo_autorizacao_teletrabalho_edit,
        name="protocolo_autorizacao_teletrabalho_edit",
    ),
    # servidor
    path("servidor/", views.servidor, name="servidor"),
    path("servidor-avaliacoes/", views.servidor_avaliacoes, name="servidor_avaliacoes"),
    path(
        "servidor-avaliacao-atividades-list/<int:pk>",
        views.servidor_avaliacao_atividades_list,
        name="servidor_avaliacao_atividades_list",
    ),
    # chefia imediata
    path("chefia-imediata/", views.chefia_imediata, name="chefia_imediata"),
    # avaliar manifestacoes interesse
    path(
        "chefia-imediata-manifestacoes-interesse/",
        views.chefia_imediata_analisar_manifestacoes,
        name="chefia_imediata_analisar_manifestacoes",
    ),
    # avaliar planos de trabalho
    path(
        "chefia-imediata-planos-trabalho/",
        views.chefia_imediata_analisar_planos_trabalho,
        name="chefia_imediata_analisar_planos_trabalho",
    ),
    # realizar avaliacoes mensais
    path(
        "chefia-imediata-avaliacoes-mensais/",
        views.chefia_imediata_realizar_avaliacoes_mensais,
        name="chefia_imediata_realizar_avaliacoes_mensais",
    ),
    # avaliacoes chefia imediata
    path("avaliacoes-chefia/", views.avaliacoes_chefia, name="avaliacoes_chefia"),
    path(
        "avaliacoes-chefia/edit/<int:pk>",
        views.avaliacao_chefia_edit,
        name="avaliacao_chefia_edit",
    ),
    path(
        "avaliacao-atividades-list/<int:pk>",
        views.avaliacao_atividades_list,
        name="avaliacao_atividades_list",
    ),
    path(
        "avaliacao-chefia-atividade/<int:pk>",
        views.avaliacao_chefia_atividade,
        name="avaliacao_chefia_atividade",
    ),
    path(
        "avaliacao-chefia-atividade/finalizar/<int:pk>",
        views.finalizar_avaliacao,
        name="finalizar_avaliacao",
    ),
    path(
        "avaliacao-chefia-alterar/<int:pk>",
        views.chefia_imediata_alterar_avaliacao_mensal,
        name="chefia_imediata_alterar_avaliacao_mensal",
    ),
    # chefia imediata controle mensal teletrabalho
    path(
        "chefia-controle-mensal-teletrabalho/",
        views.chefia_imediata_controle_mensal,
        name="chefia_imediata_controle_mensal",
    ),
    # chefia imediata controle mensal teletrabalho cancela periodo
    path(
        "chefia-imediata-controle-mensal-cancelar_periodo/<int:pk>",
        views.chefia_imediata_controle_mensal_cancelar_periodo,
        name="chefia_imediata_controle_mensal_cancelar_periodo",
    ),
    # gabinete
    path("gabinete/", views.gabinete, name="gabinete"),
    # download arquivos
    path("download/<str:model>/<int:pk>", views.download_docx, name="download_docx"),
    # htmx
    path(
        "htmx-adiciona-periodo/",
        views.htmx_adiciona_periodo,
        name="htmx_adiciona_periodo",
    ),
    path(
        "htmx-adiciona-periodo-edit/<int:pk>",
        views.htmx_adiciona_periodo_edit,
        name="htmx_adiciona_periodo_edit",
    ),
    path(
        "htmx-adiciona-atividade",
        views.htmx_adiciona_atividade,
        name="htmx_adiciona_atividade",
    ),
    path(
        "htmx-adiciona-atividade-edit/<int:pk>",
        views.htmx_adiciona_atividade_edit,
        name="htmx_adiciona_atividade_edit",
    ),
]
