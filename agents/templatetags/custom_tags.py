from django import template

register = template.Library()


@register.filter
def get_range_until(start, end):
    return range(start, end + 1)
