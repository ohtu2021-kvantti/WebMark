from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Molecule


@login_required
def view_molecule(request, molecule_id):
    m = Molecule.objects.get(pk=molecule_id)
    data = {'molecule': m}
    return render(request, 'WebCLI/molecule.html', data)
