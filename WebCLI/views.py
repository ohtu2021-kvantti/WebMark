from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput, IntegerField, FloatField, Form
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
    algorithm = Algorithm.objects.filter(molecule=molecule_id).order_by('name')
    return render(request, 'WebCLI/index.html', {'algorithms': algorithm})


def algorithm_list_by_type(request):
    type_id = Algorithm_type.objects.filter(type_name=request.GET.get("attribute")).first()
    algorithm = Algorithm.objects.filter(algorithm_type=type_id).order_by('name')
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


class MetricsForm(Form):
    iterations = IntegerField(required=False)
    measurements = IntegerField(required=False)
    circuit_depth = IntegerField(required=False)
    accuracy = FloatField(required=False)


def new_algorithm(request):
    form = AlgorithmForm(initial={'timestamp': timezone.now(), 'user': request.user})
    if request.method == "POST":
        a = AlgorithmForm(request.POST)
        a.save()
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'form': form}
    return render(request, 'WebCLI/newAlgorithm.html', data)


def algorithm_details_view(request):
    algorithm = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != algorithm.user.pk:
        raise PermissionDenied

    return render(request, 'WebCLI/algorithm.html', {'algorithm': algorithm})


class MoleculeListView(generic.ListView):
    model = Molecule
    context_object_name = "molecules"
    queryset = Molecule.objects.all()
    template_name = "WebCLI/index.html"


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


def add_metrics(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        form = MetricsForm(request.POST).data
        if form['iterations']:
            a.iterations = form['iterations']
        else:
            a.iterations = None
        if form['measurements']:
            a.measurements = form['measurements']
        else:
            a.measurements = None
        if form['circuit_depth']:
            a.circuit_depth = form['circuit_depth']
        else:
            a.circuit_depth = None
        if form['accuracy']:
            a.accuracy = form['accuracy']
        else:
            a.accuracy = None
        a.save()
        return redirect('/algorithm/?index='+str(a.pk))
    form = MetricsForm(initial={'iterations': a.iterations, 'measurements': a.measurements,
                                'circuit_depth': a.circuit_depth, 'accuracy': a.accuracy})
    data = {'algorithm': a, 'form': form}
    return render(request, 'WebCLI/addMetrics.html', data)
