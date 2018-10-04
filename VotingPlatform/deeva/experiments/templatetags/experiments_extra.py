from django import template
register = template.Library()



@register.filter(name='mult')
def cut(value, arg):
    return value*arg



