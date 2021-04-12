from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from ..models import Algorithm, Algorithm_version
from ..forms import AlgorithmVersionForm
from ..misc.analyze_options import optimizer_methods, optimizer_modules


def add_version(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        version = AlgorithmVersionForm(request.POST)
        if version.is_valid():
            version.save()
            return redirect(a)
        else:
            form = version
            data = {'algorithm': a, 'form': form}
            return render(request, 'WebCLI/addVersion.html', data)
    last_version = Algorithm_version.objects.filter(algorithm_id=a).order_by('-timestamp')[0]
    initial = {'algorithm': last_version.algorithm,
               'circuit': last_version.circuit,
               'optimizer_module': last_version.optimizer_module,
               'optimizer_method': last_version.optimizer_method,
               'timestamp': timezone.now(),
               'algorithm_id': a}
    form = AlgorithmVersionForm(initial=initial)
    data = {'algorithm': a, 'form': form}
    return render(request, 'WebCLI/addVersion.html', data)


def load_methods(request):
    module = request.GET.get('module')
    if module in optimizer_modules():
        return render(request, 'WebCLI/methods_of_module.html',
                      {'methods': optimizer_methods(module)})
    return render(request, 'WebCLI/methods_of_module.html', {'methods': []})
