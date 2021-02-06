from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput, IntegerField, FloatField, Form
from django_tables2.columns.base import Column
from .models import Algorithm, Molecule, Algorithm_type
from django.utils import timezone
from django_filters import ChoiceFilter, FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table


def home_view(request):
    return render(request, 'WebCLI/index.html')


class AlgorithmFilter(FilterSet):
    molecule_choices = [(m.name, m.name) for m in Molecule.objects.all()]
    algorithm_type_choices = [(a.type_name, a.type_name) for a in Algorithm_type.objects.all()]
    molecule = ChoiceFilter(
        field_name='molecule__name',
        choices=molecule_choices,
        empty_label="All molecules"
    )
    algorithm_type = ChoiceFilter(
        field_name='algorithm_type__type_name',
        choices=algorithm_type_choices,
        empty_label="All algorithm types"
    )

    class Meta:
        model = Algorithm
        fields = ['molecule', 'algorithm_type']


class AlgorithmTable(Table):
    name = Column(linkify=True)

    class Meta:
        model = Algorithm
        exclude = ("id", "public", "algorithm")


class AlgorithmListView(SingleTableMixin, FilterView):
    model = Algorithm
    template_name = "WebCLI/index.html"
    paginate_by = 5
    context_object_name = 'algorithms'
    queryset = Algorithm.objects.filter(public=True)
    filterset_class = AlgorithmFilter
    table_class = AlgorithmTable


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


def algorithm_details_view(request, algorithm_id):
    algorithm = Algorithm.objects.get(pk=algorithm_id)
    if request.user.pk != algorithm.user.pk:
        raise PermissionDenied

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
        return redirect(a)
    form = MetricsForm(initial={'iterations': a.iterations, 'measurements': a.measurements,
                                'circuit_depth': a.circuit_depth, 'accuracy': a.accuracy})
    data = {'algorithm': a, 'form': form}
    return render(request, 'WebCLI/addMetrics.html', data)
