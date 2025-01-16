from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if dictionary and key is not None:
        return dictionary.get(key, '0.00')
    return '0.00'





@register.filter
def dict_item(dictionary, key):
    return dictionary.get(key, '0.00')

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Devuelve el valor del diccionario para una clave dada."""
    return dictionary.get(key)

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Obtiene un valor de un diccionario usando una clave."""
    if dictionary:
        return dictionary.get(key)
    return None





register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Accede a un valor dentro de un diccionario"""
    return dictionary.get(key,None)


