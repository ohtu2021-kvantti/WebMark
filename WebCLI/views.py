from WebMark.settings import ALGORITHMS_PER_PAGE
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput, IntegerField, FloatField, Form, CharField, ValidationError
from django_tables2.columns.base import Column
from django_tables2.columns import TemplateColumn
from .models import Algorithm, Molecule, Algorithm_type, Algorithm_version
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters import AllValuesFilter, FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table
from django.core.validators import MinValueValidator
from django.utils.translation import gettext as _


class AlgorithmFilter(FilterSet):
    molecule = AllValuesFilter(
        field_name='molecule__name',
        empty_label='All molecules'
    )
    algorithm_type = AllValuesFilter(
        field_name='algorithm_type__type_name',
        empty_label="All algorithm types"
    )

    class Meta:
        model = Algorithm
        fields = ['molecule', 'algorithm_type']


class AlgorithmTable(Table):
    name = Column(linkify=True)
    github_link = Column(verbose_name='Github')
    article_link = Column(verbose_name='Article')
    pk = TemplateColumn(verbose_name='Compare',
                        template_name="WebCLI/compare.html", orderable=False)
#    timestamp = DateTimeColumn(format='d.m.Y', verbose_name='Date')

    class Meta:
        model = Algorithm
        exclude = ('id', 'public')
        attrs = {'class': 'table table-hover table-sm'}

    def render_github_link(self, value):
        return format_html(f'<a href={value}>Github</a>')

    def render_article_link(self, value):
        return format_html(f'<a href={value}>Article</a>')


class AlgorithmListView(SingleTableMixin, FilterView):
    model = Algorithm
    template_name = "WebCLI/index.html"
    paginate_by = ALGORITHMS_PER_PAGE
    context_object_name = 'algorithms'
    queryset = Algorithm.objects.filter(public=True).order_by("name")
    filterset_class = AlgorithmFilter
    table_class = AlgorithmTable


class MyAlgorithmListView(AlgorithmListView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(MyAlgorithmListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Algorithm.objects.filter(user=self.request.user).order_by("name")


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user', 'name', 'algorithm_type', 'molecule', 'public',
                  'article_link', 'github_link']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
            'user': HiddenInput(),
        }


class AlgorithmVersionForm(Form):
    algorithm = CharField(widget=Textarea)


class MetricsForm(Form):
    iterations = IntegerField(required=False, min_value=0)
    measurements = IntegerField(required=False, min_value=0)
    circuit_depth = IntegerField(required=False, min_value=0)
    accuracy = FloatField(required=False, min_value=0.0)

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
        v = Algorithm_version(timestamp=timezone.now(), algorithm_id=new_algorithm,
                              algorithm=algorithm)
        v.save()
    data = {'algorithms': Algorithm.objects.filter(user=request.user), 'aform': aform,
            'vform': vform}
    return render(request, 'WebCLI/newAlgorithm.html', data)


def algorithm_details_view(request, algorithm_id):
    algorithm = Algorithm.objects.get(pk=algorithm_id)

    if not algorithm.public and request.user.pk != algorithm.user.pk:
        raise PermissionDenied

    versions = Algorithm_version.objects.filter(algorithm_id=algorithm).order_by('-timestamp')
    selectedVersion = versions[0]
    if request.method == "POST":
        selectedVersion = Algorithm_version.objects.get(pk=request.POST.get('item_id'))
    data = {'algorithm': algorithm, 'versions': versions, 'selectedVersion': selectedVersion}
    return render(request, 'WebCLI/algorithm.html', data)


class MoleculeForm(ModelForm):
    class Meta:
        model = Molecule
        fields = ['name', 'structure']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
        }


@login_required
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


@login_required
def new_algorithm_type(request):
    form = AlgorithmTypeForm()
    if request.method == "POST":
        m = AlgorithmTypeForm(request.POST)
        m.save()
    data = {'types': Algorithm_type.objects.all(), 'form': form}
    return render(request, 'WebCLI/newAlgorithmType.html', data)


@login_required
def add_metrics(request):
    av = Algorithm_version.objects.get(pk=request.GET.get("index"))
    if request.user.pk != av.algorithm_id.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        form = MetricsForm(request.POST).data
        if form['iterations']:
            av.iterations = form['iterations']
            if not av.iterations.isnumeric():
                raise ValidationError(
                    _('Metrics input needs to be numeric; "%(value)s" was not numeric'),
                    params={'value': av.iterations},
                )
            elif int(av.iterations) < 0:
                raise ValidationError('Input value must be positive')
        else:
            av.iterations = None
        if form['measurements']:
            av.measurements = form['measurements']
            if not av.measurements.isnumeric():
                raise ValidationError(
                    _('Metrics input needs to be numeric; "%(value)s" was not numeric'),
                    params={'value': av.measurements},
                )
            elif int(av.measurements) < 0:
                raise ValidationError('Input value must be positive')
        else:
            av.measurements = None
        if form['circuit_depth']:
            av.circuit_depth = form['circuit_depth']
            if not av.circuit_depth.isnumeric():
                raise ValidationError(
                    _('Metrics input needs to be numeric; "%(value)s" was not numeric'),
                    params={'value': av.circuit_depth},
                )
            elif int(av.circuit_depth) < 0:
                raise ValidationError('Input value must be positive')
        else:
            av.circuit_depth = None
        if form['accuracy']:
            av.accuracy = form['accuracy']
            if not av.accuracy.isnumeric():
                raise ValidationError(
                    _('Metrics input needs to be numeric; "%(value)s" was not numeric'),
                    params={'value': av.accuracy},
                )
            elif int(av.accuracy) < 0:
                raise ValidationError('Input value must be positive')
        else:
            av.accuracy = None
        av.save()
        return redirect(av.algorithm_id)
    form = MetricsForm(initial={'iterations': av.iterations, 'measurements': av.measurements,
                                'circuit_depth': av.circuit_depth, 'accuracy': av.accuracy})
    data = {'algorithm': av.algorithm_id, 'version': av, 'form': form}
    return render(request, 'WebCLI/addMetrics.html', data)


def add_version(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        algorithm = AlgorithmVersionForm(request.POST).data['algorithm']
        version = Algorithm_version(algorithm_id=a, timestamp=timezone.now(), algorithm=algorithm)
        version.save()
        return redirect(a)
    last_version = Algorithm_version.objects.filter(algorithm_id=a).order_by('-timestamp')[0]
    form = AlgorithmVersionForm(initial={'algorithm': last_version.algorithm})
    data = {'algorithm': a, 'form': form}
    return render(request, 'WebCLI/addVersion.html', data)


def compare_algorithms(request, a1_id, a2_id):
    if not a1_id.isnumeric() or not a2_id.isnumeric():  # ignore garbage values
        return redirect("home")

    queryset = Algorithm.objects.filter(pk=a1_id) | Algorithm.objects.filter(pk=a2_id)
    if len(queryset) != 2:  # check that we have found two unique algorithms
        return redirect("home")

    (versions1, versions2) = (
        Algorithm_version.objects.filter(algorithm_id=queryset[0]).order_by('-timestamp'),
        Algorithm_version.objects.filter(algorithm_id=queryset[1]).order_by('-timestamp')
    )

    (av1, av2) = (versions1[0], versions2[0])
    if request.method == "POST":
        av1_id = request.POST.get('item1_id')
        av2_id = request.POST.get('item2_id')
        if av1_id:
            av1 = Algorithm_version.objects.get(pk=av1_id)
        if av2_id:
            av2 = Algorithm_version.objects.get(pk=av2_id)

    # dummy data
    graph_data = [[0, 0, 0], [1, 2, 4], [2, 4, 8], [3, 6, 10], [4, 6, 10]]
    (a1, a2) = queryset
    algo_data = [["Algorithm comparison", a1.name, a2.name],
                 ["Iterations", av1.iterations, av2.iterations],
                 ["Measurements", av1.measurements, av2.measurements],
                 ["Circuit depth", av1.circuit_depth, av2.circuit_depth],
                 ["Accuracy", av1.accuracy, av2.accuracy]]

    if not a1.public and request.user.pk != a1.user.pk:
        raise PermissionDenied
    if not a2.public and request.user.pk != a2.user.pk:
        raise PermissionDenied

    return render(request, 'WebCLI/compareAlgorithms.html',
                  {'a1': a1, 'av1': av1, 'a2': a2, 'av2': av2,
                   'versions1': versions1, 'versions2': versions2,
                   'graph_data': graph_data, 'algo_data': algo_data})
