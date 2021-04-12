from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import Molecule
from ..forms import MoleculeForm


@login_required
def new_molecule(request):
    form = MoleculeForm()
    if request.method == "POST":
        m = MoleculeForm(request.POST)
        if m.is_valid():
            m.save()
            return redirect('newMolecule')
        else:
            form = m
    data = {'molecules': Molecule.objects.all(), 'form': form}
    return render(request, 'WebCLI/newMolecule.html', data)
