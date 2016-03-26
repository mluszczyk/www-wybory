from django import template

register = template.Library()


def format_percent(a, b):
    percent = "{0:.2f}".format(100 * a / b)
    return percent


@register.inclusion_tag('wyniki/row.html')
def row(numer, nazwa, liczba_a, liczba_b, cls=''):
    vote_sum = liczba_a + liczba_b
    context = {
        'numer': numer,
        'nazwa': nazwa,
        'liczba_a': liczba_a,
        'liczba_b': liczba_b,
        'procent_a': format_percent(liczba_a, vote_sum),
        'procent_b': format_percent(liczba_b, vote_sum),
        'liczba_waznych_glosow': vote_sum,
        'cls': cls
    }
    return context