from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from ..models import Algorithm, Molecule, Algorithm_version, Metrics
from django.db.models import F


def get_algorithm_details_view_params(request):
    if request.GET.get("version_id"):
        try:
            version_id = int(request.GET.get("version_id"))
        except ValueError:
            version_id = None
    else:
        version_id = None

    if request.GET.get("metrics_id"):
        try:
            metrics_id = int(request.GET.get("metrics_id"))
        except ValueError:
            metrics_id = None
    else:
        metrics_id = None

    if request.GET.get("molecule_id"):
        try:
            molecule_id = int(request.GET.get("molecule_id"))
        except ValueError:
            molecule_id = None
    else:
        molecule_id = None

    return {
        "version_id": version_id,
        "metrics_id": metrics_id,
        "molecule_id": molecule_id
    }


def get_metrics(params, versions):
    if params["version_id"]:
        return Metrics.objects.filter(algorithm_version__pk=params["version_id"])
    else:
        return Metrics.objects.filter(algorithm_version=versions[0])


def get_selected_metrics(params, metrics):
    if params["metrics_id"]:
        for metric in metrics:
            if params["metrics_id"] == metric.pk:
                return Metrics.objects.get(pk=params["metrics_id"])

    if len(metrics) > 0:
        params["metrics_id"] = metrics[0].pk
        return metrics[0]
    else:
        return None


def get_selected_version(params, versions):
    if params["version_id"]:
        return Algorithm_version.objects.get(pk=params["version_id"])
    else:
        params["version_id"] = versions[0].pk
        return versions[0]


def get_selected_molecule(params, molecules_with_metrics):
    if params["molecule_id"]:
        return Molecule.objects.get(pk=params["molecule_id"])
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
            metrics.iterations, metrics.measurements, metrics.circuit_depth, metrics.accuracy
            FROM "WebCLI_algorithm_version" version
            LEFT JOIN "WebCLI_metrics" metrics ON metrics.algorithm_version_id = version.id
            AND metrics.molecule_id = %s
            WHERE version.algorithm_id_id = %s''', [selected_molecule.pk, algorithm.pk])

        return [[row.row_num, row.iterations, row.measurements, row.circuit_depth, row.accuracy]
                for row in metrics_graph_data_query]
    return []


def algorithm_details_view(request, algorithm_id):
    algorithm = Algorithm.objects.get(pk=algorithm_id)

    if not algorithm.public and request.user.pk != algorithm.user.pk:
        raise PermissionDenied

    versions = Algorithm_version.objects.filter(algorithm_id=algorithm).order_by('-timestamp')
    params = get_algorithm_details_view_params(request)
    metrics = get_metrics(params, versions)
    selected_metrics = get_selected_metrics(params, metrics)
    selected_version = get_selected_version(params, versions)
    molecules_with_metrics = get_molecules_with_metrics(versions)
    selected_molecule = get_selected_molecule(params, molecules_with_metrics)
    metrics_graph_data = get_metrics_graph_data(selected_molecule, algorithm)

    data = {'algorithm': algorithm, 'versions': versions, 'params': params,
            'metrics_graph_data': metrics_graph_data, 'metrics': metrics,
            'molecules_with_metrics': molecules_with_metrics,
            'selected_version': selected_version,
            'selected_metrics': selected_metrics,
            'selected_molecule': selected_molecule}

    return render(request, 'WebCLI/algorithm.html', data)
