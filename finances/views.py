from __future__ import annotations

from functools import cached_property

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, View

from .forms import AccountForm, CategoryForm, GoalForm, StatementImportForm, TransactionForm
from .models import Account, AccountType
from .selectors import (
    get_accounts_with_balances,
    get_all_transactions,
    get_category_by_id,
    get_goal_by_id,
    get_transaction_by_id,
    get_user_categories,
    get_user_goals,
)
from .services import (
    create_category,
    create_goal,
    create_transaction,
    delete_category,
    delete_goal,
    delete_transaction,
    process_bank_statement_import,
    update_category,
    update_goal,
    update_transaction,
)


class TransactionListView(LoginRequiredMixin, ListView):
    template_name = "finances/transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 8

    def get_queryset(self):
        return get_all_transactions(
            user=self.request.user,
            start_date=self.request.GET.get("start_date") or None,
            end_date=self.request.GET.get("end_date") or None,
            query=self.request.GET.get("q") or None,
            category_id=self.request.GET.get("category") or None,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = get_user_categories(user=self.request.user)
        return context


class TransactionCreateView(LoginRequiredMixin, FormView):
    template_name = "finances/transaction_form.html"
    form_class = TransactionForm
    success_url = reverse_lazy("finances:transaction_list")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["account"].queryset = self.request.user.accounts.all()
        form.fields["category"].queryset = self.request.user.categories.all()
        return form

    def form_valid(self, form):
        try:
            create_transaction(user=self.request.user, **form.cleaned_data)
            messages.success(self.request, "Movimentacao criada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class TransactionUpdateView(LoginRequiredMixin, FormView):
    template_name = "finances/transaction_form.html"
    form_class = TransactionForm
    success_url = reverse_lazy("finances:transaction_list")

    @property
    def transaction_obj(self):
        try:
            return get_transaction_by_id(user=self.request.user, transaction_id=self.kwargs["pk"])
        except Exception as exc:
            raise Http404("Transacao nao encontrada") from exc

    def get_initial(self):
        obj = self.transaction_obj
        return {
            "valor": obj.valor,
            "data": obj.data,
            "tipo": obj.tipo,
            "descricao": obj.descricao,
            "account": obj.account,
            "category": obj.category,
        }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["account"].queryset = self.request.user.accounts.all()
        form.fields["category"].queryset = self.request.user.categories.all()
        return form

    def form_valid(self, form):
        try:
            update_transaction(
                transaction_obj=self.transaction_obj,
                user=self.request.user,
                **form.cleaned_data,
            )
            messages.success(self.request, "Movimentacao atualizada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class TransactionDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            tx = get_transaction_by_id(user=request.user, transaction_id=kwargs["pk"])
            delete_transaction(transaction_obj=tx, user=request.user)
            messages.success(request, "Movimentacao excluida com sucesso.")
        except Exception:
            messages.error(request, "Nao foi possivel excluir esta movimentacao.")
        return redirect("finances:transaction_list")


class StatementImportView(LoginRequiredMixin, FormView):
    template_name = "finances/statement_import_form.html"
    form_class = StatementImportForm
    success_url = reverse_lazy("finances:transaction_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            created = process_bank_statement_import(
                form.cleaned_data["statement_file"],
                self.request.user,
                form.cleaned_data["account"],
            )
            messages.success(self.request, f"Importacao concluida com {len(created)} movimentacoes.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class CategoryListView(LoginRequiredMixin, ListView):
    template_name = "finances/category_list.html"
    context_object_name = "categories"
    paginate_by = 8

    def get_queryset(self):
        return get_user_categories(user=self.request.user)


class CategoryCreateView(LoginRequiredMixin, FormView):
    template_name = "finances/category_form.html"
    form_class = CategoryForm
    success_url = reverse_lazy("finances:category_list")

    def form_valid(self, form):
        try:
            create_category(user=self.request.user, **form.cleaned_data)
            messages.success(self.request, "Categoria criada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class CategoryUpdateView(LoginRequiredMixin, FormView):
    template_name = "finances/category_form.html"
    form_class = CategoryForm
    success_url = reverse_lazy("finances:category_list")

    @property
    def category_obj(self):
        try:
            return get_category_by_id(user=self.request.user, category_id=self.kwargs["pk"])
        except Exception as exc:
            raise Http404("Categoria nao encontrada") from exc

    def get_initial(self):
        category = self.category_obj
        return {
            "nome": category.nome,
            "tipo": category.tipo,
            "keywords": category.keywords,
        }

    def form_valid(self, form):
        try:
            update_category(category=self.category_obj, user=self.request.user, **form.cleaned_data)
            messages.success(self.request, "Categoria atualizada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class CategoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            category = get_category_by_id(user=request.user, category_id=kwargs["pk"])
            delete_category(category=category, user=request.user)
            messages.success(request, "Categoria excluida com sucesso.")
        except Exception:
            messages.error(request, "Nao foi possivel excluir esta categoria.")
        return redirect("finances:category_list")


class GoalListView(LoginRequiredMixin, ListView):
    template_name = "finances/goal_list.html"
    context_object_name = "goals"
    paginate_by = 8

    def get_queryset(self):
        return get_user_goals(user=self.request.user)


class GoalCreateView(LoginRequiredMixin, FormView):
    template_name = "finances/goal_form.html"
    form_class = GoalForm
    success_url = reverse_lazy("finances:goal_list")

    def form_valid(self, form):
        try:
            create_goal(user=self.request.user, **form.cleaned_data)
            messages.success(self.request, "Meta criada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class GoalUpdateView(LoginRequiredMixin, FormView):
    template_name = "finances/goal_form.html"
    form_class = GoalForm
    success_url = reverse_lazy("finances:goal_list")

    @property
    def goal_obj(self):
        try:
            return get_goal_by_id(user=self.request.user, goal_id=self.kwargs["pk"])
        except Exception as exc:
            raise Http404("Meta nao encontrada") from exc

    def get_initial(self):
        goal = self.goal_obj
        return {
            "nome": goal.nome,
            "valor_alvo": goal.valor_alvo,
            "valor_atual": goal.valor_atual,
        }

    def form_valid(self, form):
        try:
            update_goal(goal=self.goal_obj, user=self.request.user, **form.cleaned_data)
            messages.success(self.request, "Meta atualizada com sucesso.")
            return super().form_valid(form)
        except Exception as exc:
            form.add_error(None, str(exc))
            return self.form_invalid(form)


class GoalDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            goal = get_goal_by_id(user=request.user, goal_id=kwargs["pk"])
            delete_goal(goal=goal, user=request.user)
            messages.success(request, "Meta excluida com sucesso.")
        except Exception:
            messages.error(request, "Nao foi possivel excluir esta meta.")
        return redirect("finances:goal_list")


class AccountBaseListView(LoginRequiredMixin, ListView):
    template_name = "finances/account_list.html"
    context_object_name = "accounts"
    account_type = None
    title = "Contas"
    paginate_by = 8

    def get_queryset(self):
        return get_accounts_with_balances(user=self.request.user, tipo=self.account_type)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context["account_type"] = self.account_type
        return context


class AccountCheckingListView(AccountBaseListView):
    account_type = AccountType.CONTA_CORRENTE
    title = "Contas Correntes"


class AccountCreditCardListView(AccountBaseListView):
    account_type = AccountType.CARTAO_CREDITO
    title = "Cartoes de Credito"


class AccountBaseCreateView(LoginRequiredMixin, FormView):
    template_name = "finances/account_form.html"
    form_class = AccountForm
    account_type = None

    def dispatch(self, request, *args, **kwargs):
        if self.account_type is None:
            raise Http404("Tipo de conta nao configurado")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {"tipo": self.account_type}

    def get_success_url(self):
        if self.account_type == AccountType.CARTAO_CREDITO:
            return reverse_lazy("finances:account_credit_card_list")
        return reverse_lazy("finances:account_checking_list")

    def form_valid(self, form):
        account = form.save(commit=False)
        account.user = self.request.user
        account.tipo = self.account_type
        account.save()
        messages.success(self.request, "Conta criada com sucesso.")
        return super().form_valid(form)


class AccountCheckingCreateView(AccountBaseCreateView):
    account_type = AccountType.CONTA_CORRENTE


class AccountCreditCardCreateView(AccountBaseCreateView):
    account_type = AccountType.CARTAO_CREDITO


class AccountBaseUpdateView(LoginRequiredMixin, FormView):
    template_name = "finances/account_form.html"
    form_class = AccountForm
    account_type = None

    @cached_property
    def account_obj(self):
        account = Account.objects.filter(
            user=self.request.user,
            pk=self.kwargs["pk"],
            tipo=self.account_type,
        ).first()
        if not account:
            raise Http404("Conta nao encontrada")
        return account

    def get_initial(self):
        return {"nome": self.account_obj.nome, "tipo": self.account_obj.tipo}

    def get_success_url(self):
        if self.account_type == AccountType.CARTAO_CREDITO:
            return reverse_lazy("finances:account_credit_card_list")
        return reverse_lazy("finances:account_checking_list")

    def form_valid(self, form):
        self.account_obj.nome = form.cleaned_data["nome"]
        self.account_obj.tipo = form.cleaned_data["tipo"]
        self.account_obj.full_clean()
        self.account_obj.save()
        messages.success(self.request, "Conta atualizada com sucesso.")
        return super().form_valid(form)


class AccountCheckingUpdateView(AccountBaseUpdateView):
    account_type = AccountType.CONTA_CORRENTE


class AccountCreditCardUpdateView(AccountBaseUpdateView):
    account_type = AccountType.CARTAO_CREDITO


class AccountBaseDeleteView(LoginRequiredMixin, View):
    account_type = None

    def post(self, request, *args, **kwargs):
        account = Account.objects.filter(
            user=request.user,
            pk=kwargs["pk"],
            tipo=self.account_type,
        ).first()
        if account:
            account.delete()
            messages.success(request, "Conta excluida com sucesso.")
        if self.account_type == AccountType.CARTAO_CREDITO:
            return redirect("finances:account_credit_card_list")
        return redirect("finances:account_checking_list")


class AccountCheckingDeleteView(AccountBaseDeleteView):
    account_type = AccountType.CONTA_CORRENTE


class AccountCreditCardDeleteView(AccountBaseDeleteView):
    account_type = AccountType.CARTAO_CREDITO
