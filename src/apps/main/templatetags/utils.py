from django import template
from .. import models


register = template.Library()


@register.simple_tag
def get_site_settings():
    return models.SiteSettings.get_solo()


@register.simple_tag
def get_excursion_list():
    return models.Excursion.objects.all()


@register.simple_tag
def get_review_list():
    return models.Review.objects.all()


@register.simple_tag
def get_faq_list():
    return models.FAQ.objects.all()


@register.filter
def index(list_obj, i):
    try:
        return list_obj[int(i)]
    finally:
        return ""
