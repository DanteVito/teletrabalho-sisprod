from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm, inlineformset_factory

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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ManifestacaoInteresseForm, self).__init__(*args, **kwargs)

        self.fields['servidor'] = forms.ModelChoiceField(
            queryset=User.objects.filter(id=self.user.id),
            initial=User.objects.filter(
                id=self.user.id).first(),
            widget=forms.Select(),
        )

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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(DeclaracaoNaoEnquadramentoVedacoesForm,
              self).__init__(*args, **kwargs)

        self.fields['manifestacao'] = forms.ModelChoiceField(
            queryset=ManifestacaoInteresse.objects.filter(servidor=self.user),
            initial=ManifestacaoInteresse.objects.filter(
                servidor=self.user).last(),
            widget=forms.Select(),
        )

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
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PlanoTrabalhoForm,
              self).__init__(*args, **kwargs)

        self.fields['manifestacao'] = forms.ModelChoiceField(
            queryset=ManifestacaoInteresse.objects.filter(servidor=self.user),
            initial=ManifestacaoInteresse.objects.filter(
                servidor=self.user).last(),
            widget=forms.Select(),
        )

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
            'periodo',
            'atividade',
            'meta_qualitativa',
            'tipo_meta_quantitativa',
            'meta_quantitativa',
            'cumprimento',
            'justificativa_nao_cumprimento'
        )


class CustomPeriodoTeletrabalhoFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            cleaned_data = form.cleaned_data
            data_fim = cleaned_data.get('data_fim')
            data_inicio = cleaned_data.get('data_inicio')
            if not data_fim > data_inicio:
                raise forms.ValidationError(
                    "A data final não pode ser anterior à data inicial!")
            return cleaned_data


PeriodoTeletrabalhoFormSet = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    fields=(
        'plano_trabalho',
        'data_inicio',
        'data_fim',
    ),
    extra=1,
    can_delete=False
)


PeriodoTeletrabalhoFormSetCreate = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    fields=(
        'data_inicio',
        'data_fim',
    ),
    formset=CustomPeriodoTeletrabalhoFormset,
    extra=3,
    can_delete=False
)


AtividadesTeletrabalhoFormSet = inlineformset_factory(
    PeriodoTeletrabalho,
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


class AvaliacaoChefiaFinalizaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = ('finalizar_avaliacao', )
