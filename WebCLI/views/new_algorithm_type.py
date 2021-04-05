from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from ..models import Algorithm_type
from ..forms import AlgorithmTypeForm


@login_required
def new_algorithm_type(request):
    form = AlgorithmTypeForm()
    if request.method == "POST":
        m = AlgorithmTypeForm(request.POST)
        m.save()
        return HttpResponseRedirect('/newAlgorithmType/')
    data = {'types': Algorithm_type.objects.all(), 'form': form}
    return render(request, 'WebCLI/newAlgorithmType.html', data)
