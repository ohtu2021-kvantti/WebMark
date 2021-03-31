from django.shortcuts import redirect
from ..models import Molecule, Algorithm_version
from WebCLI.celery.task_sender import send_benchmark_task
from django.forms.models import model_to_dict


def test_algorithm(request):
    version = model_to_dict(Algorithm_version.objects.get(pk=request.GET.get("version")))
    molecule = model_to_dict(Molecule.objects.get(pk=request.GET.get("molecule")))
    data = {'molecule': molecule, 'version': version}
    send_benchmark_task(data)
    print(version.circuit)
    print(molecule.structure)
    return redirect('/myAlgorithms/')
