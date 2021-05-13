import itertools
from typing import Optional, Type, Dict, List, Any, Iterable, Union, Tuple

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import QuerySet
from django.views import View

from WebCLI.models import Algorithm_version, Metrics, Algorithm, Accuracy_history, Average_history
from django.db.models.expressions import RawSQL


class AlgorithmViewBase(View):
    """
    Base class for algorithm details view and algorithm comparison view.
    Provides common functionality for these views.
    """

    def to_positive_int_or_none(self, value: Any) -> Optional[int]:
        """
        Turns the value into a positive integer or None if that cannot be done.

        Parameters
        ----------
        value
            value to check, can be anything
        Returns
        -------
        value
            value or None if value is not a positive integer
        """
        if not value:
            return None
        try:
            int_value = int(value)
            return int_value if int_value > 0 else None
        except ValueError:
            return None

    def get_params(self, request: Type[WSGIRequest], keys: List[str]) -> Dict[str, Optional[int]]:
        """
        Parameters
        ----------
        request
            WSGIRequest
        keys
            list of strings

        Returns
        -------
        dict
            A dictionary with the given keys and matching values from request params.
            Only positive integers are accepted and other values are turned into None.
        """
        return {k: self.to_positive_int_or_none(request.GET.get(k)) for k in keys}

    def get_versions_with_version_number(self, algorithm: Type[Algorithm]) -> Type[QuerySet]:
        """
        For the given algorithm, returns a list of algorithm versions annotated
        with ascending version numbers.

        Parameters
        ----------
        algorithm
            algorithm whose algorithm versions are to be returned
        Returns
        -------
        queryset
            list of algorithm versions annotated with ascending version numbers
        """
        query = Algorithm_version.objects.filter(algorithm_id=algorithm)
        query = query.annotate(version_number=RawSQL("ROW_NUMBER() OVER(ORDER BY timestamp)", []))
        query = query.order_by('-timestamp')
        return query

    def get_selected_version(
            self,
            version_id: Optional[int],
            versions) -> Optional[Type[Algorithm_version]]:
        if not version_id:
            return versions[0]
        try:
            return Algorithm_version.objects.get(pk=version_id)
        except Algorithm_version.DoesNotExist:
            return None

    def get_metrics(
            self,
            version_id: Optional[int],
            versions: Union[List[Type[Metrics]], Type[QuerySet]]) -> List[Type[Metrics]]:
        if version_id:
            return Metrics.objects.filter(algorithm_version__pk=version_id)
        else:
            return Metrics.objects.filter(algorithm_version=versions[0])

    def get_selected_metrics(self, metric_id, metrics) -> Optional[Type[Metrics]]:
        if metric_id and any(metric.pk == metric_id for metric in metrics):
            return Metrics.objects.get(pk=metric_id)

        if len(metrics) > 0:
            return metrics[0]
        return None

    def get_history_graph_data(
            self,
            history_model: Union[Type[Accuracy_history], Type[Average_history]],
            selected_metrics: List[Optional[Type[QuerySet]]]) -> Iterable:
        """
        Parameters
        ----------
        history_model
            Django model that contains history data (can be Accuracy_history or Average_history)
        selected_metrics
            list of metrics that the history data belongs to

        Returns
        -------
        list
            a list of tuples where the first element is the number of the iteration
            and the following elements are the values on that iteration on all given metrics
        """
        if all(selected_metrics):
            history_data = []
            for metrics in selected_metrics:
                data = history_model.objects.values_list("data", flat=True)  # TODO: n+1 problem?
                data = data.filter(metrics=metrics)
                history_data.append(data)
            return self.histories_to_graph_data(history_data)
        return []

    def histories_to_graph_data(self, history_data: List[List[float]]) -> List[Tuple]:
        """
        A helper function that turns a list of history data into a format that is
        suitable for drawing a graph. If the histories have different lengths because
        the algorithms took different amount of iterations to complete, the lists are
        padded with None values.

        For example, input [[0, 0.5, 1], [0.1, 0.2]]
        turns into [(1, 0, 0.1), (2, 0.5, 0.2), (3, 1, None)]

        Parameters
        ----------
        history_data
            List of history data for different algorithms.
        Returns
        -------
        list
            A list of tuples where the first element is the number of the iteration
            and the following elements are the values on that iteration on all given metrics.
        """
        graph_data_length = max([len(lst) for lst in history_data])
        iterations = list(range(1, graph_data_length + 1))
        return list(itertools.zip_longest(iterations, *history_data))
