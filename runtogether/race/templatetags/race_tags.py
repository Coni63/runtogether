from django import template

register = template.Library()

STATUS_STYLES = {
    "not_open": {"class": "bg-slate-800", "label": "Non ouvertes"},
    "open": {"class": "bg-green-500", "label": "En cours"},
    "closed": {"class": "bg-orange-500", "label": "Terminées"},
    "terminated": {"class": "bg-red-500", "label": "Course terminée"},
}

RACE_TYPE_STYLES = {
    "road": {"class": "bg-slate-800", "label": "Road"},
    "trail": {"class": "bg-green-500", "label": "Trail"},
}


@register.inclusion_tag("race/tags/status_chip.html")
def status_chip(value):
    config = STATUS_STYLES.get(value, {"class": "chip-gray", "label": "Inconnu"})
    return config


@register.inclusion_tag("race/tags/status_chip.html")
def race_type_chip(value):
    config = RACE_TYPE_STYLES.get(value, {"class": "chip-gray", "label": "Inconnu"})
    return config
