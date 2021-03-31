from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Molecule
from ..forms import MoleculeForm


@login_required
def new_molecule(request):
    form = MoleculeForm()
    if request.method == "POST":
        m = MoleculeForm(request.POST)
        print(m)
        if m.is_valid():
            m.save()
        else:
            form = m
    data = {'molecules': Molecule.objects.all(), 'form': form}
    return render(request, 'WebCLI/newMolecule.html', data)
