from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Algorithm
from ..forms import AlgorithmForm


def update_algorithm(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        form = AlgorithmForm(request.POST, instance=a)
        form.save()
        return redirect(a)
    return render(request, 'WebCLI/updateDetails.html', {'form': AlgorithmForm(instance=a)})
