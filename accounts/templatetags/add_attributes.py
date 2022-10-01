from django import template
import json

register = template.Library()

@register.filter(name="add_attributes")
def add_attributes(value, arg):
    # print(f"--->{value}")
    # print(f"--->{arg}")

    new_attrs = eval(arg)

    # get all the default attributes 
    attributes = value.field.widget.attrs.items()
    # print(attributes)

    # # convert dict_items to dictionary
    new_attributes = dict(attributes)
    # print(new_attributes)

    # # update attributes dictionary
    new_attributes.update(new_attrs)

    # print(new_attributes)
    # print(list(new_attributes.items()))
    
    # # convert attributes to list of tuple
    attributes = list(new_attributes.items()) 

    return value.as_widget(attrs=attributes)