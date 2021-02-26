from django import template
register = template.Library()


@register.inclusion_tag("WebCLI/moleculeSelectorForm.html")
def molecule_selector_form(form_name, select_name, molecules, selected_molecule, 
                           version1, version2):
    return {'form_name': form_name, 'select_name': select_name,
            'molecules': molecules, 'selectedMolecule': selected_molecule,
            'version1': version1, 'version2': version2}
