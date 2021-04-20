from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from ..models import Algorithm, Algorithm_version
from ..forms import AlgorithmForm
from ..forms import AlgorithmVersionForm
from ..misc.analyze_options import optimizer_modules


@login_required
def new_algorithm(request):
    aform = AlgorithmForm(initial={'user': request.user})
    vform = AlgorithmVersionForm(initial={'optimizer_module': optimizer_modules()[0]})
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
            avf = AlgorithmVersionForm(request.POST)
            nv = Algorithm_version(timestamp=timezone.now(),
                                   algorithm_id=new_algorithm,
                                   algorithm=avf.data['algorithm'],
                                   circuit=avf.data['circuit'],
                                   optimizer_module=avf.data['optimizer_module'],
                                   optimizer_method=avf.data['optimizer_method'])
            nv.save()
            return redirect('newAlgorithm')
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'aform': aform,
            'vform': vform}
    return render(request, 'WebCLI/newAlgorithm.html', data)
