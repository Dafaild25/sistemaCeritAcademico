from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Accede a un valor dentro de un diccionario"""
    return dictionary.get(key)
