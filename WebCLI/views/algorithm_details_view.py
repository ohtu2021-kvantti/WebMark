from django.db.models.expressions import RawSQL
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from ..models import Algorithm, Molecule, Algorithm_version
from ..models import Average_history, Metrics
from django.db.models import F


def to_positive_int_or_none(value):
    if not value:
        return None
    try:
        int_value = int(value)
        return int_value if int_value > 0 else None
    except ValueError:
        return None


def get_algorithm_details_view_params(request):
    version_id = to_positive_int_or_none(request.GET.get("version_id"))
    metrics_id = to_positive_int_or_none(request.GET.get("metrics_id"))
    molecule_id = to_positive_int_or_none(request.GET.get("molecule_id"))

    return {
        "version_id": version_id,
        "metrics_id": metrics_id,
        "molecule_id": molecule_id
    }


def get_versions(algorithm):
    query = Algorithm_version.objects.filter(algorithm_id=algorithm)
    query = query.annotate(version_number=RawSQL("ROW_NUMBER() OVER(ORDER BY timestamp)", []))
    query = query.order_by('-timestamp')
    return query


def get_metrics(params, versions):
    if params["version_id"]:
        return Metrics.objects.filter(algorithm_version__pk=params["version_id"])
    else:
        return Metrics.objects.filter(algorithm_version=versions[0])


def get_selected_metrics(params, metrics):
    metric_id = params["metrics_id"]
    if metric_id and any(metric.pk == metric_id for metric in metrics):
        return Metrics.objects.get(pk=metric_id)

    if len(metrics) > 0:
        params["metrics_id"] = metrics[0].pk
        return metrics[0]
    return None


def get_selected_version(params, versions):
    if params["version_id"]:
        try:
            return Algorithm_version.objects.get(pk=params["version_id"])
        except Algorithm_version.DoesNotExist:
            return None
    else:
        params["version_id"] = versions[0].pk
        return versions[0]


def get_selected_molecule(params, molecules_with_metrics):
    if params["molecule_id"]:
        try:
            return Molecule.objects.get(pk=params["molecule_id"])
        except Molecule.DoesNotExist:
            return None

    elif len(molecules_with_metrics) > 0:
        selected_molecule = Molecule.objects.get(pk=molecules_with_metrics[0]["pk"])
        params["molecule_id"] = selected_molecule.pk
        return selected_molecule


def get_molecules_with_metrics(versions):
    query = Metrics.objects.filter(algorithm_version__in=versions)
    query = query.distinct("molecule_id")
    return query.values(pk=F("molecule_id"), name=F("molecule__name"))


def get_metrics_graph_data(selected_molecule, algorithm):
    if selected_molecule:
        metrics_graph_data_query = Metrics.objects.raw('''
            SELECT metrics.id, ROW_NUMBER() OVER(ORDER BY version.timestamp) as row_num,
            metrics.gate_depth, metrics.qubit_count, metrics.average_iterations,
            metrics.success_rate
            FROM "WebCLI_algorithm_version" version
            LEFT JOIN "WebCLI_metrics" metrics ON metrics.algorithm_version_id = version.id
            AND metrics.molecule_id = %s
            WHERE version.algorithm_id_id = %s''', [selected_molecule.pk, algorithm.pk])

        return [[row.row_num, row.gate_depth, row.qubit_count, row.average_iterations,
                 row.success_rate]
                for row in metrics_graph_data_query]
    return []


def get_avg_history_graph_data(selected_metrics):
    if selected_metrics:
        avg_history_graph_data_query = Average_history.objects.raw('''
            SELECT avg_his.id, avg_his.iteration_number,
            avg_his.data
            FROM "WebCLI_average_history" avg_his
            LEFT JOIN "WebCLI_metrics" metrics ON avg_his.analyzed_results_id = metrics.id
            WHERE metrics.id = %s''', [selected_metrics.pk])

        return [[row.iteration_number, row.data]
                for row in avg_history_graph_data_query]
    return []


def algorithm_details_view(request, algorithm_id):
    try:
        algorithm = Algorithm.objects.get(pk=algorithm_id)
    except Algorithm.DoesNotExist:
        return redirect("home")

    if not algorithm.public and request.user.pk != algorithm.user.pk:
        raise PermissionDenied

    versions = get_versions(algorithm)
    params = get_algorithm_details_view_params(request)
    metrics = get_metrics(params, versions)
    selected_metrics = get_selected_metrics(params, metrics)
    selected_version = get_selected_version(params, versions)
    molecules_with_metrics = get_molecules_with_metrics(versions)
    selected_molecule = get_selected_molecule(params, molecules_with_metrics)
    metrics_graph_data = get_metrics_graph_data(selected_molecule, algorithm)
    avg_history_graph_data = get_avg_history_graph_data(selected_metrics)
    molecules = Molecule.objects.all()

    data = {'algorithm': algorithm, 'versions': versions, 'params': params,
            'metrics_graph_data': metrics_graph_data, 'metrics': metrics,
            'avg_history_graph_data': avg_history_graph_data,  
            'molecules_with_metrics': molecules_with_metrics,
            'selected_version': selected_version,
            'selected_metrics': selected_metrics,
            'selected_molecule': selected_molecule,
            'molecules': molecules}

    return render(request, 'WebCLI/algorithm.html', data)
