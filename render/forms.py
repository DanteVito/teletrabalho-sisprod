from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, ModelForm, inlineformset_factory

from authentication.models import User

from .models import (
    AlterarAvaliacaoChefia,
    AtividadesTeletrabalho,
    AutorizacoesExcecoes,
    AvaliacaoChefia,
    Cargo,
    DeclaracaoNaoEnquadramentoVedacoes,
    Lotacao,
    ManifestacaoInteresse,
    PeriodoTeletrabalho,
    PlanoTrabalho,
    PortariasPublicadasDOE,
    PostosTrabalho,
    ProtocoloAutorizacaoTeletrabalho,
    Servidor,
)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "nome",
            "rg",
        )


class ServidorForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        servidor = Servidor.objects.get(user=self.user)
        super(ServidorForm, self).__init__(*args, **kwargs)

        self.fields["user"] = forms.ModelChoiceField(
            queryset=User.objects.filter(id=self.user.id),
            initial=User.objects.filter(id=self.user.id).first(),
        )

        self.fields["cargo"] = forms.ModelChoiceField(
            queryset=Cargo.objects.filter(id=servidor.cargo.id),
            initial=Cargo.objects.filter(id=servidor.cargo.id).first(),
        )

    class Meta:
        model = Servidor
        fields = (
            "user",
            "cargo",
            "ramal",
            "celular",
            "email",
            "cidade",
        )
        widgets = {
            "ramal": forms.TextInput(attrs={"class": "input"}),
            "celular": forms.TextInput(attrs={"class": "input"}),
            "email": forms.TextInput(attrs={"class": "input"}),
            "cidade": forms.TextInput(attrs={"class": "input"}),
        }


class LotacaoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        servidor = Servidor.objects.get(user=self.user)
        super(LotacaoForm, self).__init__(*args, **kwargs)

        self.fields["servidor"] = forms.ModelChoiceField(
            queryset=Servidor.objects.filter(id=servidor.id),
            initial=Servidor.objects.filter(id=servidor.id).first(),
            widget=forms.Select(),
        )

        self.fields["posto_trabalho"] = forms.ModelChoiceField(
            queryset=PostosTrabalho.objects.all(),
            widget=forms.Select(),
        )

    class Meta:
        model = Lotacao
        fields = ("servidor", "posto_trabalho")


class ManifestacaoInteresseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        lotacao = Lotacao.objects.get(servidor__user__id=self.user.id)
        super(ManifestacaoInteresseForm, self).__init__(*args, **kwargs)

        self.fields["lotacao_servidor"] = forms.ModelChoiceField(
            queryset=Servidor.objects.filter(id=lotacao.id),
            initial=Servidor.objects.filter(id=lotacao.id).first(),
            widget=forms.Select(),
        )

    class Meta:
        model = ManifestacaoInteresse
        fields = ("lotacao_servidor",)
        # widgets = {
        #     'funcao': forms.TextInput(attrs={'class': 'input'}),
        #     'funcao_chefia': forms.TextInput(attrs={'class': 'input'}),
        # }


class ManifestacaoInteresseAprovadoChefiaForm(ModelForm):
    class Meta:
        model = ManifestacaoInteresse
        fields = ("aprovado_chefia", "justificativa_chefia")
        widgets = {
            "justificativa_chefia": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "cols": "30",
                    "rows": "10",
                    "placeholder": "Justificativa para aceitação/não aceitação ...",
                }
            ),
        }


class DeclaracaoNaoEnquadramentoVedacoesForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(DeclaracaoNaoEnquadramentoVedacoesForm, self).__init__(*args, **kwargs)
        servidor = Servidor.objects.get(user=self.user)

        self.fields["manifestacao"] = forms.ModelChoiceField(
            queryset=ManifestacaoInteresse.objects.filter(
                lotacao_servidor__servidor=servidor
            ),
            initial=ManifestacaoInteresse.objects.filter(
                lotacao_servidor__servidor=servidor
            ).last(),
            widget=forms.Select(),
        )

    class Meta:
        model = DeclaracaoNaoEnquadramentoVedacoes
        fields = (
            "manifestacao",
            "estagio_probatorio",
            "cargo_chefia_direcao",
            "penalidade_disciplinar",
            "justificativa_excecao",
        )
        widgets = {
            "estagio_probatorio": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "cargo_chefia_direcao": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "penalidade_disciplinar": forms.CheckboxInput(attrs={"class": "checkbox"}),
            "justificativa_excecao": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "cols": "30",
                    "rows": "10",
                    "placeholder": "Justificativas para concessão de teletrabalho para ocupantes de cargo de chefia ou direção ...",
                }
            ),
        }


class PlanoTrabalhoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super(PlanoTrabalhoForm, self).__init__(*args, **kwargs)

        if not self.user.groups.filter(name="CIGT"):
            self.fields["manifestacao"] = forms.ModelChoiceField(
                queryset=ManifestacaoInteresse.objects.filter(
                    lotacao_servidor__servidor__user=self.user
                ),
                initial=ManifestacaoInteresse.objects.filter(
                    lotacao_servidor__servidor__user=self.user
                ).last(),
                widget=forms.Select(),
            )

        for field_name, field in self.fields.items():
            field.widget.attrs["data-field"] = field_name

    class Meta:
        model = PlanoTrabalho
        fields = (
            "manifestacao",
            "periodo_comparecimento",
            "periodo_acionamento",
            "sistemas",
        )
        widgets = {
            "periodo_comparecimento": forms.TextInput(attrs={"class": "input"}),
            "periodo_acionamento": forms.TextInput(attrs={"class": "input"}),
        }


class PlanoTrabalhoFormAprovadoChefiaForm(ModelForm):
    class Meta:
        model = PlanoTrabalho
        fields = ("aprovado_chefia",)


class PlanoTrabalhoFormAprovadoCIGTForm(ModelForm):
    class Meta:
        model = PlanoTrabalho
        fields = ("aprovado_cigt",)


class PeriodoTeletrabalhoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PeriodoTeletrabalhoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["data-field"] = field_name

    class Meta:
        model = PeriodoTeletrabalho
        fields = (
            "plano_trabalho",
            "data_inicio",
            "data_fim",
        )
        widgets = {
            "plano_trabalho": forms.HiddenInput(attrs={"data-field": "plano_trabalho"}),
            "data_inicio": forms.DateInput(attrs={"class": "input", "type": "date"}),
            "data_fim": forms.DateInput(attrs={"class": "input", "type": "date"}),
        }


class AtividadesTeletrabalhoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AtividadesTeletrabalhoForm, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs["data-field"] = field_name

    class Meta:
        model = AtividadesTeletrabalho
        fields = (
            "periodo",
            "atividade",
            "meta_qualitativa",
            "tipo_meta_quantitativa",
            "meta_quantitativa",
        )
        widgets = {
            "periodo": forms.HiddenInput(attrs={"data-field": "periodo"}),
            "meta_qualitativa": forms.TextInput(
                attrs={"class": "input", "data-field": "meta_qualitativa"}
            ),
            "meta_quantitativa": forms.TextInput(
                attrs={"class": "input", "data-field": "meta_quantitativa"}
            ),
        }


class CustomPeriodoTeletrabalhoFormset(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            cleaned_data = form.cleaned_data
            data_fim = cleaned_data.get("data_fim")
            data_inicio = cleaned_data.get("data_inicio")
            if not data_fim > data_inicio:
                raise forms.ValidationError(
                    "A data final não pode ser anterior à data inicial!"
                )
            return cleaned_data


PeriodoTeletrabalhoFormSet = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    fields=(
        "plano_trabalho",
        "data_inicio",
        "data_fim",
    ),
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    widgets={
        "plano_trabalho": forms.HiddenInput(attrs={"data-field": "plano_trabalho"}),
        "data_inicio": forms.DateInput(
            attrs={"class": "input", "type": "date", "data-field": "data_inicio"}
        ),
        "data_fim": forms.DateInput(
            attrs={"class": "input", "type": "date", "data-field": "data_fim"}
        ),
    },
)


PeriodoTeletrabalhoFormSetCreate = inlineformset_factory(
    PlanoTrabalho,
    PeriodoTeletrabalho,
    fields=(
        "data_inicio",
        "data_fim",
    ),
    formset=CustomPeriodoTeletrabalhoFormset,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    widgets={
        "data_inicio": forms.DateInput(attrs={"class": "input", "type": "date"}),
        "data_fim": forms.DateInput(attrs={"class": "input", "type": "date"}),
    },
)


AtividadesTeletrabalhoFormSet = inlineformset_factory(
    PeriodoTeletrabalho,
    AtividadesTeletrabalho,
    extra=0,
    min_num=1,
    validate_min=True,
    can_delete=False,
    fields=(
        "periodo",
        "atividade",
        "meta_qualitativa",
        "tipo_meta_quantitativa",
        "meta_quantitativa",
    ),
    widgets={
        "periodo": forms.HiddenInput(attrs={"data-field": "periodo"}),
        "atividade": forms.Select(attrs={"data-field": "atividade"}),
        "meta_qualitativa": forms.TextInput(
            attrs={"class": "input", "data-field": "meta_qualitativa"}
        ),
        "tipo_meta_quantitativa": forms.Select(
            attrs={"data-field": "tipo_meta_quantitativa"}
        ),
        "meta_quantitativa": forms.TextInput(
            attrs={"class": "input", "data-field": "meta_quantitativa"}
        ),
    },
)

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
            "declaracao",
            "aprovado_gabinete",
        )


class AutorizacoesExcecoesAprovaForm(ModelForm):
    class Meta:
        model = AutorizacoesExcecoes
        fields = ("aprovado_gabinete",)


class ProtocoloAutorizacaoTeletrabalhoForm(ModelForm):
    class Meta:
        model = ProtocoloAutorizacaoTeletrabalho
        fields = (
            "sid",
            "publicado_doe",
        )
        widgets = {"sid": forms.TextInput(attrs={"class": "input"})}


class ProtocoloAutorizacaoTeletrabalhoAprovaForm(ModelForm):
    class Meta:
        model = ProtocoloAutorizacaoTeletrabalho
        fields = (
            "despacho_cigt",
            "sid",
            "publicado_doe",
        )


class AvaliacaoChefiaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = (
            "atestado_cumprimento_metas",
            "justificativa_nao_cumprimento",
        )


class AvaliacaoChefiaFinalizaForm(ModelForm):
    class Meta:
        model = AvaliacaoChefia
        fields = ("finalizar_avaliacao",)


class AtividadeCumprimentoForm(ModelForm):
    class Meta:
        model = AtividadesTeletrabalho
        fields = ("cumprimento",)
        widgets = {"cumprimento": forms.Select(attrs={"class": "input"})}


class AlterarAvaliacaoChefiaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.avaliacao = kwargs.pop("avaliacao")
        super(AlterarAvaliacaoChefiaForm, self).__init__(*args, **kwargs)

        self.fields["avaliacao_chefia"] = forms.ModelChoiceField(
            queryset=AvaliacaoChefia.objects.filter(id=self.avaliacao.id),
            initial=AvaliacaoChefia.objects.filter(id=self.avaliacao.id).first(),
        )

    class Meta:
        model = AlterarAvaliacaoChefia
        fields = (
            "avaliacao_chefia",
            "justificativa",
        )
        widgets = {
            "avaliação": forms.Select(attrs={"class": "input"}),
            "justificativa": forms.Textarea(
                attrs={
                    "class": "textarea",
                    "cols": "30",
                    "rows": "10",
                    "placeholder": "Justificativa para alteração ...",
                }
            ),
        }


class PortariaDoeEditForm(ModelForm):
    class Meta:
        model = PortariasPublicadasDOE
        fields = ("ano", "numero", "diretor_em_exercicio", "data_publicacao")
        widgets = {
            "ano": forms.NumberInput(attrs={"class": "input"}),
            "numero": forms.NumberInput(attrs={"class": "input"}),
            "diretor_em_exercicio": forms.TextInput(attrs={"class": "input"}),
            "data_publicacao": forms.DateInput(
                attrs={"class": "input", "type": "date"}
            ),
        }
