from WebMark.settings import ALGORITHMS_PER_PAGE, ROOT_DIR
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.html import format_html
from django_tables2.columns.base import Column
from django_tables2.columns import TemplateColumn
from ..models import Algorithm, Molecule, Algorithm_type, Algorithm_version, Metrics
from .forms import AlgorithmForm, AlgorithmTypeForm
from .forms import MoleculeForm, AlgorithmVersionForm, MetricsForm, TestCircuitForm
from django.utils import timezone
from django.utils.decorators import method_decorator
from django_filters import AllValuesFilter, FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table
from django.http import HttpResponseBadRequest


class AlgorithmFilter(FilterSet):
    algorithm_type = AllValuesFilter(
        field_name='algorithm_type__type_name',
        empty_label="All algorithm types"
    )

    class Meta:
        model = Algorithm
        fields = ['algorithm_type']


class AlgorithmTable(Table):
    name = Column(linkify=True)
    github_link = Column(verbose_name='Github')
    article_link = Column(verbose_name='Article')
    pk = TemplateColumn(verbose_name='Compare',
                        template_name="WebCLI/compare.html", orderable=False)

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

    def get_context_data(self, **kwargs):
        context = super(AlgorithmListView, self).get_context_data(**kwargs)
        context['root_dir'] = ROOT_DIR
        return context


class MyAlgorithmListView(AlgorithmListView):

    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        return super(MyAlgorithmListView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        return Algorithm.objects.filter(user=self.request.user).order_by("name")


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


@login_required
def new_molecule(request):
    form = MoleculeForm()
    if request.method == "POST":
        m = MoleculeForm(request.POST)
        m.save()
    data = {'molecules': Molecule.objects.all(), 'form': form}
    return render(request, 'WebCLI/newMolecule.html', data)


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
        for f in ['iterations', 'measurements', 'circuit_depth', 'accuracy']:
            if form[f]:
                data = form[f]
                try:
                    number = float(data)
                    if number < 0:
                        return HttpResponseBadRequest('Input value must be positive')
                except ValueError:
                    return HttpResponseBadRequest('Metrics input needs to be numeric')
        m = Molecule.objects.get(pk=int(form['molecule']))
        existing = Metrics.objects.filter(algorithm_version=av, molecule=m)
        if len(existing) > 0:
            metrics = MetricsForm(request.POST, instance=existing[0])
            metrics.save()
        else:
            metrics = MetricsForm(request.POST)
            metrics.save()
        return redirect(av.algorithm_id)
    form = MetricsForm(initial={'algorithm_version': av, 'verified': False})
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


def update_algorithm(request):
    a = Algorithm.objects.get(pk=request.GET.get("index"))
    if request.user.pk != a.user.pk:
        raise PermissionDenied

    if request.method == "POST":
        form = AlgorithmForm(request.POST, instance=a)
        form.save()
        return redirect(a)
    return render(request, 'WebCLI/updateDetails.html', {'form': AlgorithmForm(instance=a)})


def compare_algorithms(request, a1_id, a2_id):

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
            av2 = Algorithm_version.objects.get(pk=request.POST.get('otherVersion'))
        if av2_id:
            av2 = Algorithm_version.objects.get(pk=av2_id)
            av1 = Algorithm_version.objects.get(pk=request.POST.get('otherVersion'))

    molecules1 = Metrics.objects.filter(algorithm_version=av1).values('molecule')
    molecules2 = Metrics.objects.filter(algorithm_version=av2).values('molecule')
    common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))
    selected_molecule = None
    if len(common_molecules) > 0:
        selected_molecule = common_molecules[0]

    if request.method == "POST" and request.POST.get('item3_id'):
        selected_molecule = Molecule.objects.get(pk=request.POST.get('item3_id'))
        av1 = Algorithm_version.objects.get(pk=request.POST.get('version1'))
        av2 = Algorithm_version.objects.get(pk=request.POST.get('version2'))
        molecules1 = Metrics.objects.filter(algorithm_version=av1).values('molecule')
        molecules2 = Metrics.objects.filter(algorithm_version=av2).values('molecule')
        common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))

    metrics1 = None
    metrics2 = None
    graph_data = None
    algo_data = None
    (a1, a2) = queryset
    if selected_molecule is not None:
        metrics1 = Metrics.objects.get(algorithm_version=av1, molecule=selected_molecule)
        metrics2 = Metrics.objects.get(algorithm_version=av2, molecule=selected_molecule)

        # dummy data
        graph_data = [[0, 0, 0], [1, 2, 4], [2, 4, 8], [3, 6, 10], [4, 6, 10]]
        algo_data = [["Algorithm comparison", a1.name, a2.name],
                     ["Iterations", metrics1.iterations, metrics2.iterations],
                     ["Measurements", metrics1.measurements, metrics2.measurements],
                     ["Circuit depth", metrics1.circuit_depth, metrics2.circuit_depth],
                     ["Accuracy", metrics1.accuracy, metrics2.accuracy]]

    if ((not a1.public and request.user.pk != a1.user.pk) or
       (not a2.public and request.user.pk != a2.user.pk)):
        raise PermissionDenied

    return render(request, 'WebCLI/compareAlgorithms.html',
                  {'a1': a1, 'av1': av1, 'a2': a2, 'av2': av2,
                   'metrics1': metrics1, 'metrics2': metrics2,
                   'common_molecules': common_molecules, 'molecule': selected_molecule,
                   'versions1': versions1, 'versions2': versions2,
                   'graph_data': graph_data, 'algo_data': algo_data})

def test_circuit(request):
        res = "No change made"
        if request.method == "POST":
            res = print(TestCircuitForm(request.POST).data['circuit'])
        gates = {1:'CNOT', 2:'CRx', 3:'CRy', 4:'CRz', 5:'CX', 6:'CY', 7:'CZ',
                 8: 'ExpPauli', 9:'GeneralizedRotation', 10:'H', 11:'Phase',
                 12: 'PowerGate', 13:'QGate', 14:'RotationGate', 15:'Rp', 16:'Rx',
                 17: 'Ry', 18:'Rz', 19:'S', 20:'SWAP', 21:'T', 22:'Toffoli', 
                 23: 'Trotterized', 24: 'X', 25: 'Y', 26: 'Z', 27: 'wrap_gate'}
        print(len(gates))
        return render(request, 'WebCLI/circuit.html', {'form': TestCircuitForm(), 'gates':gates})