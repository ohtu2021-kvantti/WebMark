from django.shortcuts import render
# from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput
from .models import Algorithm, Molecule, Algorithm_type
from django.utils import timezone

def home_view(request):
    return render(request, 'WebCLI/index.html')


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user','timestamp', 'name', 'algorithm_type', 'molecule', 'public', 'algorithm']
        widgets = {
            'name': Textarea(attrs={'rows':1, 'cols':50}),
            'user': HiddenInput(),
            'timestamp': HiddenInput(),
        }


def algorithm_view(request):
    form = AlgorithmForm(initial={'timestamp': timezone.now(), 'user': request.user})
    if request.method == "POST":
        a = AlgorithmForm(request.POST)
        a.save()
    return render(request, 'WebCLI/newAlgorithm.html', {'algorithms': Algorithm.objects.filter(user=request.user), 'form': form})


class MoleculeForm(ModelForm):
    class Meta:
        model = Molecule
        fields = ['name', 'structure']
        widgets = {
            'name': Textarea(attrs={'rows':1, 'cols':50}),
        }


def molecule_view(request):
    form = MoleculeForm()
    if request.method == "POST":
        m = MoleculeForm(request.POST)
        m.save()
    return render(request, 'WebCLI/newMolecule.html', {'molecules': Molecule.objects.all(), 'form': form})


class AlgorithmTypeForm(ModelForm):
    class Meta:
        model = Algorithm_type
        fields = ['type_name']
        widgets = {
            'type_name': Textarea(attrs={'rows':1, 'cols':50}),
        }


def algorithm_type_view(request):
    form = AlgorithmTypeForm()
    if request.method == "POST":
        m = AlgorithmTypeForm(request.POST)
        m.save()
    return render(request, 'WebCLI/newAlgorithmType.html', {'types': Algorithm_type.objects.all(), 'form': form})