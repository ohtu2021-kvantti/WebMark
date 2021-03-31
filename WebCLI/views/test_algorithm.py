from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Molecule, Algorithm_version
from WebCLI.celery import celery_app
from django.forms.models import model_to_dict

def test_algorithm(request):
    version =  model_to_dict(Algorithm_version.objects.get(pk=request.GET.get("version")))
    molecule =  model_to_dict(Molecule.objects.get(pk=request.GET.get("molecule")))
    data = {'molecule': molecule, 'version': version}
    celery_app.send_task("benchmark.benchmark_task", args=[data])
    print(version.circuit)
    print(molecule.structure)
    return redirect('/myAlgorithms/')