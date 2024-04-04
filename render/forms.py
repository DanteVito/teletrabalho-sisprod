from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm, inlineformset_factory

from authentication.models import User

from .models import (AtividadesTeletrabalho, AutorizacoesExcecoes,
                     AvaliacaoChefia, DeclaracaoNaoEnquadramentoVedacoes,
                     ManifestacaoInteresse, PeriodoTeletrabalho, PlanoTrabalho,
                     PortariasPublicadasDOE, ProtocoloAutorizacaoTeletrabalho)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = (
            'ramal',
            'celular',
            'email',
            'cidade',
        )
        widgets = {
            'ramal': forms.NumberInput(attrs={'class': 'input'}),
            'celular': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.EmailInput(attrs={'class': 'input'}),
            'cidade': forms.TextInput(attrs={'class': 'input'}),
        }


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
        widgets = {
            'funcao': forms.TextInput(attrs={'class': 'input'}),
            'funcao_chefia': forms.TextInput(attrs={'class': 'input'}),
        }


class ManifestacaoInteresseAprovadoChefiaForm(ModelForm):
    class Meta:
        model = ManifestacaoInteresse
        fields = (
            'aprovado_chefia',
            'justificativa_chefia'
        )
        widgets = {
            'justificativa_chefia': forms.Textarea(attrs={'class': 'textarea', 'cols': '30', 'rows': '10', 'placeholder': 'Justificativa para aceitação/não aceitação ...'}),
        }


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
        widgets = {
            'estagio_probatorio': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'cargo_chefia_direcao': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'penalidade_disciplinar': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'justificativa_excecao': forms.Textarea(attrs={'class': 'textarea', 'cols': '30', 'rows': '10', 'placeholder': 'Justificativas para concessão de teletrabalho para ocupantes de cargo de chefia ou direção ...'}),
        }


class PlanoTrabalhoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(PlanoTrabalhoForm,
              self).__init__(*args, **kwargs)

        if not self.user.groups.filter(name="CIGT"):
            self.fields['manifestacao'] = forms.ModelChoiceField(
                queryset=ManifestacaoInteresse.objects.filter(
                    servidor=self.user),
                initial=ManifestacaoInteresse.objects.filter(
                    servidor=self.user).last(),
                widget=forms.Select(),
            )

        for field_name, field in self.fields.items():
            field.widget.attrs['data-field'] = field_name

    class Meta:
        model = PlanoTrabalho
        fields = (
            'manifestacao',
            'periodo_comparecimento',
            'periodo_acionamento',
            'sistemas',
        )
        widgets = {
            'periodo_comparecimento': forms.TextInput(attrs={'class': 'input'}),
            'periodo_acionamento': forms.TextInput(attrs={'class': 'input'}),
        }


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
    def __init__(self, *args, **kwargs):
        super(PeriodoTeletrabalhoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['data-field'] = field_name

    class Meta:
        model = PeriodoTeletrabalho
        fields = (
            'plano_trabalho',
            'data_inicio',
            'data_fim',
        )
        widgets = {
            'plano_trabalho': forms.HiddenInput(),
            'data_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'data_fim': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }


class AtividadesTeletrabalhoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AtividadesTeletrabalhoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs['data-field'] = field_name

    class Meta:
        model = AtividadesTeletrabalho
        fields = (
            'periodo',
            'atividade',
            'meta_qualitativa',
            'tipo_meta_quantitativa',
            'meta_quantitativa',
        )
        widgets = {
            'periodo': forms.HiddenInput(),
            'meta_qualitativa': forms.TextInput(attrs={'class': 'input'}),
            'meta_quantitativa': forms.TextInput(attrs={'class': 'input'}),
        }


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
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    widgets={
        'data_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        'data_fim': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
    }
)


PeriodoTeletrabalhoFormSetCreate = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    fields=(
        'data_inicio',
        'data_fim',
    ),
    formset=CustomPeriodoTeletrabalhoFormset,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    widgets={
        'data_inicio': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        'data_fim': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
    }
)


AtividadesTeletrabalhoFormSet = inlineformset_factory(
    PeriodoTeletrabalho,
    AtividadesTeletrabalho,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    fields=(
        "periodo", "atividade", "meta_qualitativa", "tipo_meta_quantitativa", "meta_quantitativa", ),
    widgets={
        'meta_qualitativa': forms.TextInput(attrs={'class': 'input'}),
        'meta_quantitativa': forms.TextInput(attrs={'class': 'input'}),
    })

# AtividadesTeletrabalhoFormSet = inlineformset_factory(
#     PeriodoTeletrabalho,
#     AtividadesTeletrabalho,
#     form=AtividadesTeletrabalhoForm,
#     extra=1,
#     can_delete=False,
#     widgets={
#         'meta_qualitativa': forms.TextInput(attrs={'class': 'input'}),
#     }
# )


class AutorizacoesExcecoesForm(ModelForm):
    class Meta:
        model = AutorizacoesExcecoes
        fields = (
            'declaracao',
            'aprovado_gabinete',
        )


class AutorizacoesExcecoesAprovaForm(ModelForm):
    class Meta:
        model = AutorizacoesExcecoes
        fields = (
            'aprovado_gabinete',
        )


class ProtocoloAutorizacaoTeletrabalhoForm(ModelForm):
    class Meta:
        model = ProtocoloAutorizacaoTeletrabalho
        fields = ('sid', 'publicado_doe', )
        widgets = {
            'sid': forms.TextInput(attrs={'class': 'input'})
        }


class ProtocoloAutorizacaoTeletrabalhoAprovaForm(ModelForm):
    class Meta:
        model = ProtocoloAutorizacaoTeletrabalho
        fields = ('despacho_cigt', 'sid', 'publicado_doe', )


class AvaliacaoChefiaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = ('atestado_cumprimento_metas',
                  'justificativa_nao_cumprimento', )


class AvaliacaoChefiaFinalizaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = ('finalizar_avaliacao', )


class AtividadeCumprimentoForm(ModelForm):
    class Meta:
        model = AtividadesTeletrabalho
        fields = ('cumprimento', )
        widgets = {
            'cumprimento': forms.Select(attrs={'class': 'input'})
        }


class PortariaDoeEditForm(ModelForm):
    class Meta:
        model = PortariasPublicadasDOE
        fields = ('ano', 'numero', 'diretor_em_exercicio', 'data_publicacao')
        widgets = {
            'ano': forms.NumberInput(attrs={'class': 'input'}),
            'numero': forms.NumberInput(attrs={'class': 'input'}),
            'diretor_em_exercicio': forms.TextInput(attrs={'class': 'input'}),
            'data_publicacao': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
        }
