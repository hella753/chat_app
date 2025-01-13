from django import template

register = template.Library()

@register.filter
def exclude_self(members, user):
    filtered_members = members.exclude(id=user.id)
    return filtered_members.first()