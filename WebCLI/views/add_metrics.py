from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest
from ..models import Molecule, Algorithm_version, Metrics
from ..forms import MetricsForm


@login_required
def add_metrics(request):
    av = Algorithm_version.objects.get(pk=request.GET.get("index"))
    if request.user.pk != av.algorithm_id.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        form = MetricsForm(request.POST).data
        for f in ['iterations', 'measurements', 'circuit_depth', 'accuracy']:
            if form[f]:
                data = form[f]
                try:
                    number = float(data)
                    if number < 0:
                        return HttpResponseBadRequest('Input value must be positive')
                except ValueError:
                    return HttpResponseBadRequest('Metrics input needs to be numeric')
        m = Molecule.objects.get(pk=int(form['molecule']))
        existing = Metrics.objects.filter(algorithm_version=av, molecule=m)
        if len(existing) > 0:
            metrics = MetricsForm(request.POST, instance=existing[0])
            metrics.save()
        else:
            metrics = MetricsForm(request.POST)
            metrics.save()
        return redirect(av.algorithm_id)
    form = MetricsForm(initial={'algorithm_version': av, 'verified': False})
    data = {'algorithm': av.algorithm_id, 'version': av, 'form': form}
    return render(request, 'WebCLI/addMetrics.html', data)
