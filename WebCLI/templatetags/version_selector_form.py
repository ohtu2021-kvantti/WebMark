from django import template
register = template.Library()


@register.inclusion_tag("WebCLI/versionSelectorForm.html")
def version_selector_form(form_name, select_name, versions, selected_version, other_version):
    return {'form_name': form_name, 'select_name': select_name,
            'versions': versions, 'selectedVersion': selected_version,
            'otherVersion': other_version}
