from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from ..models import Algorithm, Algorithm_version
from ..forms import AlgorithmVersionForm


def add_version(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        algorithm = AlgorithmVersionForm(request.POST).data['algorithm']
        circuit = AlgorithmVersionForm(request.POST).data['circuit']
        optimizer_method = AlgorithmVersionForm(request.POST).data['optimizer_method']
        optimizer_module = AlgorithmVersionForm(request.POST).data['optimizer_module']
        version = Algorithm_version(algorithm_id=a, timestamp=timezone.now(), algorithm=algorithm,
                                    circuit=circuit, optimizer_module=optimizer_module,
                                    optimizer_method=optimizer_method)
        version.save()
        return redirect(a)
    last_version = Algorithm_version.objects.filter(algorithm_id=a).order_by('-timestamp')[0]
    initial = {'algorithm': last_version.algorithm,
               'circuit': last_version.circuit,
               'optimizer_module': last_version.optimizer_module,
               'optimizer_method': last_version.optimizer_method}
    form = AlgorithmVersionForm(initial=initial)
    data = {'algorithm': a, 'form': form}
    return render(request, 'WebCLI/addVersion.html', data)
