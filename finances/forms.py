from django import forms

from .models import Account, Category, Goal, Transaction


BASE_INPUT_CLASS = (
    "w-full rounded-xl bg-zinc-900/50 border border-zinc-700 px-4 py-3 "
    "text-zinc-100 focus:outline-none focus:ring-2 focus:ring-violet-500 "
    "focus-visible:ring-emerald-400 focus-visible:ring-offset-2 focus-visible:ring-offset-zinc-950"
)


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ["valor", "data", "tipo", "descricao", "account", "category"]
        widgets = {
            "valor": forms.NumberInput(attrs={"class": BASE_INPUT_CLASS, "step": "0.01"}),
            "data": forms.DateInput(attrs={"class": BASE_INPUT_CLASS, "type": "date"}),
            "tipo": forms.Select(attrs={"class": BASE_INPUT_CLASS}),
            "descricao": forms.TextInput(attrs={"class": BASE_INPUT_CLASS}),
            "account": forms.Select(attrs={"class": BASE_INPUT_CLASS}),
            "category": forms.Select(attrs={"class": BASE_INPUT_CLASS}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["nome", "tipo", "keywords"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": BASE_INPUT_CLASS}),
            "tipo": forms.Select(attrs={"class": BASE_INPUT_CLASS}),
            "keywords": forms.Textarea(attrs={"class": BASE_INPUT_CLASS, "rows": 3}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ["nome", "tipo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": BASE_INPUT_CLASS}),
            "tipo": forms.Select(attrs={"class": BASE_INPUT_CLASS}),
        }


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ["nome", "valor_alvo", "valor_atual"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": BASE_INPUT_CLASS}),
            "valor_alvo": forms.NumberInput(attrs={"class": BASE_INPUT_CLASS, "step": "0.01"}),
            "valor_atual": forms.NumberInput(attrs={"class": BASE_INPUT_CLASS, "step": "0.01"}),
        }


class StatementImportForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        widget=forms.Select(attrs={"class": BASE_INPUT_CLASS}),
        label="Conta",
    )
    statement_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"class": BASE_INPUT_CLASS}),
        label="Arquivo de extrato",
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["account"].queryset = Account.objects.filter(user=user).order_by("nome")

    def clean_statement_file(self):
        file_obj = self.cleaned_data["statement_file"]
        name = (file_obj.name or "").lower()
        if not name.endswith((".csv", ".ofx", ".pdf")):
            raise forms.ValidationError("Formato invalido. Envie arquivo CSV, OFX ou PDF.")
        return file_obj
