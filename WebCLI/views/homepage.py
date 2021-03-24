from WebMark.settings import ALGORITHMS_PER_PAGE, ROOT_DIR
from django.utils.html import format_html
from django_tables2.columns.base import Column
from django_tables2.columns import TemplateColumn
from django_filters import AllValuesFilter, FilterSet
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin, Table
from ..models import Algorithm


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
