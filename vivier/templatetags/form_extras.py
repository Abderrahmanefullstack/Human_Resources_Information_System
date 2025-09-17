# vivier/templatetags/form_extras.py
from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(bound_field, css_classes: str):
    """
    Ajoute une/des classes CSS au widget d'un champ sans écraser l'existant.
    Usage: {{ form.myfield|add_class:"form-control is-invalid" }}
    """
    widget = bound_field.field.widget
    attrs = widget.attrs.copy()
    existing = attrs.get("class", "")
    attrs["class"] = f"{existing} {css_classes}".strip() if existing else css_classes
    return bound_field.as_widget(attrs=attrs)
