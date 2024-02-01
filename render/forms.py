from django.forms import ModelForm, inlineformset_factory

from authentication.models import User

from .models import (AtividadesTeletrabalho, AutorizacoesExcecoes,
                     AvaliacaoChefia, DeclaracaoNaoEnquadramentoVedacoes,
                     ManifestacaoInteresse, PeriodoTeletrabalho, PlanoTrabalho,
                     ProtocoloAutorizacaoTeletrabalho)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = (
            'ramal',
            'celular',
            'email',
            'cidade',
        )


class ManifestacaoInteresseForm(ModelForm):
    class Meta:
        model = ManifestacaoInteresse
        fields = (
            'servidor',
            'unidade',
            'setor',
            'funcao',
            'posto_trabalho',
            'chefia_imediata',
            'funcao_chefia',
            'posto_trabalho_chefia',
        )


class ManifestacaoInteresseAprovadoChefiaForm(ModelForm):
    class Meta:
        model = ManifestacaoInteresse
        fields = (
            'aprovado_chefia',
        )


class DeclaracaoNaoEnquadramentoVedacoesForm(ModelForm):
    class Meta:
        model = DeclaracaoNaoEnquadramentoVedacoes
        fields = (
            'manifestacao',
            'estagio_probatorio',
            'cargo_chefia_direcao',
            'penalidade_disciplinar',
            'justificativa_excecao',
        )


class PlanoTrabalhoForm(ModelForm):
    class Meta:
        model = PlanoTrabalho
        fields = (
            'manifestacao',
            'periodo_comparecimento',
            'periodo_acionamento',
            'sistemas',
        )


class PlanoTrabalhoFormAprovadoChefiaForm(ModelForm):
    class Meta:
        model = PlanoTrabalho
        fields = (
            'aprovado_chefia',
        )


class PlanoTrabalhoFormAprovadoCIGTForm(ModelForm):
    class Meta:
        model = PlanoTrabalho
        fields = (
            'aprovado_cigt',
        )


class PeriodoTeletrabalhoForm(ModelForm):
    class Meta:
        model = PeriodoTeletrabalho
        fields = (
            'plano_trabalho',
            'data_inicio',
            'data_fim',
        )


class AtividadesTeletrabalhoForm(ModelForm):
    class Meta:
        model = AtividadesTeletrabalho
        fields = (
            'plano_trabalho',
            'atividade',
            'meta_qualitativa',
            'tipo_meta_quantitativa',
            'meta_quantitativa'
        )


PeriodoTeletrabalhoFormSet = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    form=PeriodoTeletrabalhoForm,
    extra=1,
    can_delete=False
)


AtividadesTeletrabalhoFormSet = inlineformset_factory(
    PlanoTrabalho,
    AtividadesTeletrabalho,
    form=AtividadesTeletrabalhoForm,
    extra=1,
    can_delete=False
)


class AutorizacoesExcecoesForm(ModelForm):
    class Meta:
        model = AutorizacoesExcecoes
        fields = (
            'declaracao',
            'aprovado_gabinete',
        )


class ProtocoloAutorizacaoTeletrabalhoForm(ModelForm):
    class Meta:
        model = ProtocoloAutorizacaoTeletrabalho
        fields = ('sid', 'publicado_doe', )


class AvaliacaoChefiaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = ('atestado_cumprimento_metas',
                  'justificativa_nao_cumprimento', )
