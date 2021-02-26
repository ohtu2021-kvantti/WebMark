from django import template
register = template.Library()


@register.inclusion_tag("WebCLI/moleculeSelectorForm.html")
def molecule_selector_form(form_name, select_name, metrics, selected_metrics):
    return {'form_name': form_name, 'select_name': select_name,
            'metrics': metrics, 'selectedMetrics': selected_metrics}
