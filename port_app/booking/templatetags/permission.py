from django import template

register = template.Library()


@register.filter
def has_perm(user, permission):
    return user.has_perm("booking.{}".format(permission))


@register.filter
def has_perm_accounts(user, permission):
    return user.has_perm("accounts.{}".format(permission))