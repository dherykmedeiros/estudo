from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def format_money(value, currency="BRL"):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return value

    symbols = {
        "BRL": "R$",
        "USD": "$",
        "EUR": "EUR",
    }
    symbol = symbols.get(currency, "R$")

    if currency == "BRL":
        formatted = f"{amount:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        return f"{symbol} {formatted}"

    formatted = f"{amount:,.2f}"
    return f"{symbol} {formatted}"


@register.filter
def format_date(value, date_format="dd/mm/yyyy"):
    if not value:
        return value

    if date_format == "yyyy-mm-dd":
        return value.strftime("%Y-%m-%d")
    return value.strftime("%d/%m/%Y")
