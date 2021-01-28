from django.shortcuts import render
# from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm
from .models import Algorithm


def homePageView(request):
    return render(request, 'WebCLI/index.html')


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

class AlgorithmForm(ModelForm):
        class Meta:
            model = Algorithm
            fields = ['name', 'timestamp', 'public', 'algorithm', 'user', 'iterations', 'measurements', 'circuit_depth', 'accuracy']

def AlgorithmView(request):
    form = AlgorithmForm()

    if request.method == "POST":
        form = AlgorithmForm()

    return render(request, 'registration/newAlgorithm.html', {'form': form})
