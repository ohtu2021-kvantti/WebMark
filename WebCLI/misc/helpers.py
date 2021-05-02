from WebCLI.models import Algorithm_version, Metrics
from django.db.models.expressions import RawSQL


def to_positive_int_or_none(value):
    if not value:
        return None
    try:
        int_value = int(value)
        return int_value if int_value > 0 else None
    except ValueError:
        return None


def get_versions(algorithm):
    query = Algorithm_version.objects.filter(algorithm_id=algorithm)
    query = query.annotate(version_number=RawSQL("ROW_NUMBER() OVER(ORDER BY timestamp)", []))
    query = query.order_by('-timestamp')
    return query


def get_selected_version(params, param_key, versions):
    if params[param_key]:
        try:
            return Algorithm_version.objects.get(pk=params[param_key])
        except Algorithm_version.DoesNotExist:
            return None
    else:
        params[param_key] = versions[0].pk
        return versions[0]


def get_metrics(version_id, versions):
    if version_id:
        return Metrics.objects.filter(algorithm_version__pk=version_id)
    else:
        return Metrics.objects.filter(algorithm_version=versions[0])


def get_selected_metrics(params, param_key, metrics):
    metric_id = params[param_key]
    if metric_id and any(metric.pk == metric_id for metric in metrics):
        return Metrics.objects.get(pk=metric_id)

    if len(metrics) > 0:
        params[param_key] = metrics[0].pk
        return metrics[0]
    return None


def get_transformation_options():
    t = ['jordan_wigner',
         'bravyi_kitaev',
         'bravyi_kitaev_tree',
         'symmetry_conserving_bravyi_kitaev']
    return t
