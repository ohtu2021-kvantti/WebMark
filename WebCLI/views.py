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


class AlgorithmListView(generic.ListView):
    model = Algorithm
    context_object_name = "algorithms"
    queryset = Algorithm.objects.filter(public=True)
    template_name = "WebCLI/index.html"

def algorithm_list_by_molecule(request):
   
    molecule_id = Molecule.objects.filter(name=request.GET.get("attribute")).first()
    algorithm = Algorithm.objects.filter(molecule=molecule_id)
    return render(request, 'WebCLI/index.html', {'algorithms': algorithm})

def algorithm_list_by_type(request):
   
    type_id = Algorithm_type.objects.filter(type_name=request.GET.get("attribute")).first()
    algorithm = Algorithm.objects.filter(algorithm_type=type_id)
    return render(request, 'WebCLI/index.html', {'algorithms': algorithm})


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user', 'timestamp', 'name', 'algorithm_type', 'molecule', 'public',
                  'algorithm', 'article_link', 'github_link']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
            'user': HiddenInput(),
            'timestamp': HiddenInput(),
        }


def new_algorithm(request):
    form = AlgorithmForm(initial={'timestamp': timezone.now(), 'user': request.user})
    if request.method == "POST":
        a = AlgorithmForm(request.POST)
        a.save()
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'form': form}
    return render(request, 'WebCLI/newAlgorithm.html', data)


def algorithm_details_view(request):
    algorithm = Algorithm.objects.get(pk=request.GET.get("index"))
    return render(request, 'WebCLI/algorithm.html', {'algorithm': algorithm})


class MoleculeForm(ModelForm):
    class Meta:
        model = Molecule
        fields = ['name', 'structure']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
        }


def new_molecule(request):
    form = MoleculeForm()
    if request.method == "POST":
        m = MoleculeForm(request.POST)
        m.save()
    data = {'molecules': Molecule.objects.all(), 'form': form}
    return render(request, 'WebCLI/newMolecule.html', data)


class AlgorithmTypeForm(ModelForm):
    class Meta:
        model = Algorithm_type
        fields = ['type_name']
        widgets = {
            'type_name': Textarea(attrs={'rows': 1, 'cols': 50}),
        }


def new_algorithm_type(request):
    form = AlgorithmTypeForm()
    if request.method == "POST":
        m = AlgorithmTypeForm(request.POST)
        m.save()
    data = {'types': Algorithm_type.objects.all(), 'form': form}
    return render(request, 'WebCLI/newAlgorithmType.html', data)
