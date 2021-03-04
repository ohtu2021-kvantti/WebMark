from WebMark.settings import ALGORITHMS_PER_PAGE, ROOT_DIR
from django.contrib.auth.decorators import login_required
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin
from django.utils.decorators import method_decorator
from ..models import Algorithm
from .views import AlgorithmFilter, AlgorithmTable


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
