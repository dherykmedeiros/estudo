from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView

from finances.selectors import get_all_transactions


class StaffOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return bool(self.request.user and self.request.user.is_staff)


class AdminDashboardView(StaffOnlyMixin, TemplateView):
    template_name = "admin_panel/dashboard.html"


class AdminTransactionListView(StaffOnlyMixin, TemplateView):
    template_name = "admin_panel/transaction_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transactions"] = get_all_transactions(user=self.request.user)
        return context
