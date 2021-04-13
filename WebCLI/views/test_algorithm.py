from django.shortcuts import redirect
from ..models import Molecule, Algorithm_version
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from WebCLI.celery.task_sender import send_benchmark_task
from django.forms.models import model_to_dict
from WebCLI.models import Metrics
from django.contrib import messages


def create_task(request, version, existing_metrics, molecule):
    send_task = True
    if len(existing_metrics) > 0:
        metrics = existing_metrics[0]
        if metrics.in_analyze_queue:
            messages.info(request, 'Task is already in queue!')
            send_task = False
        else:
            metrics.in_analyze_queue = True
            metrics.save()
            messages.info(request, 'Algorithm version will be analyzed again')
    else:
        messages.info(request, 'Algorithm version will be analyzed')
        metrics = Metrics(
            algorithm_version=version,
            molecule=molecule,
            gate_depth=None,
            qubit_count=None,
            average_iterations=None,
            success_rate=None,
            in_analyze_queue=True)
        metrics.save()
    if send_task:
        send_benchmark_task(
            metrics.pk, model_to_dict(molecule), version.circuit,
            version.optimizer_module, version.optimizer_method
        )
    return metrics


@login_required
def test_algorithm(request):
    version = Algorithm_version.objects.get(pk=request.GET.get("version"))
    if request.user.pk != version.algorithm_id.user.pk:
        raise PermissionDenied
    molecule = Molecule.objects.get(pk=request.GET.get("molecule"))
    existing_metrics = Metrics.objects.filter(algorithm_version=version, molecule=molecule)

    metrics = create_task(request, version, existing_metrics, molecule)

    response = redirect('algorithm_details', algorithm_id=version.algorithm_id.pk)
    response['Location'] += '?version_id='+str(version.pk)+'&metrics_id='+str(metrics.pk)
    return response
