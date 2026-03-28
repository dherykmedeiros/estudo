from django.urls import path

from . import views

app_name = "finances"

urlpatterns = [
    path("transactions/", views.TransactionListView.as_view(), name="transaction_list"),
    path("transactions/import/", views.StatementImportView.as_view(), name="transaction_import"),
    path("transactions/new/", views.TransactionCreateView.as_view(), name="transaction_create"),
    path("transactions/<int:pk>/edit/", views.TransactionUpdateView.as_view(), name="transaction_update"),
    path("transactions/<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="transaction_delete"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/new/", views.CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    path("goals/", views.GoalListView.as_view(), name="goal_list"),
    path("goals/new/", views.GoalCreateView.as_view(), name="goal_create"),
    path("goals/<int:pk>/edit/", views.GoalUpdateView.as_view(), name="goal_update"),
    path("goals/<int:pk>/delete/", views.GoalDeleteView.as_view(), name="goal_delete"),
    path("accounts/contas-correntes/", views.AccountCheckingListView.as_view(), name="account_checking_list"),
    path("accounts/contas-correntes/new/", views.AccountCheckingCreateView.as_view(), name="account_checking_create"),
    path("accounts/contas-correntes/<int:pk>/edit/", views.AccountCheckingUpdateView.as_view(), name="account_checking_update"),
    path("accounts/contas-correntes/<int:pk>/delete/", views.AccountCheckingDeleteView.as_view(), name="account_checking_delete"),
    path("accounts/cartoes/", views.AccountCreditCardListView.as_view(), name="account_credit_card_list"),
    path("accounts/cartoes/new/", views.AccountCreditCardCreateView.as_view(), name="account_credit_card_create"),
    path("accounts/cartoes/<int:pk>/edit/", views.AccountCreditCardUpdateView.as_view(), name="account_credit_card_update"),
    path("accounts/cartoes/<int:pk>/delete/", views.AccountCreditCardDeleteView.as_view(), name="account_credit_card_delete"),
]
