from django import template
register = template.Library()


@register.filter(name="dict_obj")
def radio_image(value,num):
    #data = []
    #for k in value:
    #    data.append(k)

    return value[num]