from django.shortcuts import redirect
from ..models import Molecule, Algorithm_version
from WebCLI.celery.task_sender import send_benchmark_task
from django.forms.models import model_to_dict
from WebCLI.models import Metrics, Average_history


def test_algorithm(request):
    version = Algorithm_version.objects.get(pk=request.GET.get("version"))
    molecule = Molecule.objects.get(pk=request.GET.get("molecule"))
    existing_metrics = Metrics.objects.filter(algorithm_version=version, molecule=molecule)
    if len(existing_metrics) > 0:
        metrics_id = existing_metrics[0].pk
    else:
        metrics = Metrics(
            algorithm_version=version,
            molecule=molecule,
            gate_depth=None,
            qubit_count=None,
            average_iterations=None,
            success_rate=None)
        metrics.save()
        metrics_id = metrics.pk
        average_history = Average_history(
            analyzed_results=metrics_id,
            data=None,
            iteration_number=None)
        average_history.save()


    send_benchmark_task(
        metrics_id, model_to_dict(molecule), version.circuit,
        version.optimizer_module, version.optimizer_method
    )
    return redirect('myAlgorithms')
