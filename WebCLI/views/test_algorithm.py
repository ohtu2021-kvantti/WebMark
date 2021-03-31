from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Molecule, Algorithm_version
from WebCLI.celery import celery_app

def test_algorithm(request):
    version = Algorithm_version.objects.get(pk=request.GET.get("version"))
    molecule = Molecule.objects.get(pk=request.GET.get("molecule"))
    celery_app.send_task("benchmark.benchmark_task", args=[version.circuit, molecule.structure])
    print(version.circuit)
    print(molecule.structure)
    return redirect('/myAlgorithms/')