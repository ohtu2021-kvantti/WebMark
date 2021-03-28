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
        v = AlgorithmVersionForm(request.POST)
        v.timestamp = timezone.now()
        v.algorithm_id = new_algorithm
        if v.has_error('circuit'):
            aform = algorithm_form
            vform = v
        else:
            new_algorithm.save()
            new_version = Algorithm_version(timestamp=timezone.now(),
                                            algorithm_id=new_algorithm,
                                            algorithm=AlgorithmVersionForm(request.POST).data['algorithm'],
                                            circuit=AlgorithmVersionForm(request.POST).data['circuit'],
                                            optimizer_module=AlgorithmVersionForm(request.POST).data['optimizer_module'],
                                            optimizer_method=AlgorithmVersionForm(request.POST).data['optimizer_method'])
            new_version.save()
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'aform': aform,
            'vform': vform}
    return render(request, 'WebCLI/newAlgorithm.html', data)
