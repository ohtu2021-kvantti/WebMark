from django.shortcuts import redirect
from ..models import Molecule, Algorithm_version
from WebCLI.celery.task_sender import send_benchmark_task
from django.forms.models import model_to_dict


def test_algorithm(request):
    version = Algorithm_version.objects.get(pk=request.GET.get("version"))
    molecule = model_to_dict(Molecule.objects.get(pk=request.GET.get("molecule")))
    print(molecule)
    send_benchmark_task(
        molecule, version.circuit, version.optimizer_module, version.optimizer_method
    )
    return redirect('/myAlgorithms/')
