from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Molecule

@login_required
def view_molecule(request):
    m = Molecule.objects.get(pk=request.GET.get("index"))
    data = {'molecule': m}
    return render(request, 'WebCLI/molecule.html', data)