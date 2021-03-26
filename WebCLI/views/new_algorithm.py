from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Algorithm, Algorithm_version
from ..forms import AlgorithmForm
from ..forms import AlgorithmVersionForm


@login_required
def new_algorithm(request):
    aform = AlgorithmForm(initial={'user': request.user})
    vform = AlgorithmVersionForm()
    if request.method == "POST":
        algorithm_form = AlgorithmForm(request.POST)
        new_algorithm = algorithm_form.save(commit=False)
        new_algorithm.user = request.user
        new_algorithm.save()
        algorithm = AlgorithmVersionForm(request.POST).data['algorithm']
        circuit = AlgorithmVersionForm(request.POST).data['circuit']
        optimizer_module = AlgorithmVersionForm(request.POST).data['optimizer_module']
        optimizer_method = AlgorithmVersionForm(request.POST).data['optimizer_method']
        v = Algorithm_version(timestamp=timezone.now(), algorithm_id=new_algorithm,
                              algorithm=algorithm, circuit=circuit,
                              optimizer_method=optimizer_method, optimizer_module=optimizer_module)
        v.save()
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'aform': aform,
            'vform': vform}
    return render(request, 'WebCLI/newAlgorithm.html', data)
