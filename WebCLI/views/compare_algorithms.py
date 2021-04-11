from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Algorithm, Molecule, Algorithm_version, Metrics
from WebCLI.misc.helpers import to_positive_int_or_none
from django.db.models.expressions import RawSQL
from django.db.models import F


def get_comparison_view_params(request):
    version1_id = to_positive_int_or_none(request.GET.get("version1_id"))
    metrics1_id = to_positive_int_or_none(request.GET.get("metrics1_id"))
    version2_id = to_positive_int_or_none(request.GET.get("version2_id"))
    metrics2_id = to_positive_int_or_none(request.GET.get("metrics2_id"))
    molecule_id = to_positive_int_or_none(request.GET.get("molecule_id"))

    return {
        "version1_id": version1_id,
        "metrics1_id": metrics1_id,
        "version2_id": version2_id,
        "metrics2_id": metrics2_id,
        "molecule_id": molecule_id
    }


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


def get_selected_versions(params, versions1, versions2):
    version1 = get_selected_version(params, "version1_id", versions1)
    version2 = get_selected_version(params, "version2_id", versions2)
    return (version1, version2)


def get_common_molecules(versions1, versions2):
    molecules1 = Metrics.objects.filter(algorithm_version__in=versions1).values("molecule")
    molecules2 = Metrics.objects.filter(algorithm_version__in=versions2).values("molecule")
    common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))
    return common_molecules


def get_metrics(params, versions1, versions2):
    metrics1 = get_metrics_of_version(params["version1_id"], versions1)
    metrics2 = get_metrics_of_version(params["version2_id"], versions2)
    return (metrics1, metrics2)


def get_metrics_of_version(version_id, versions):
    if version_id:
        return Metrics.objects.filter(algorithm_version__pk=version_id)
    else:
        return Metrics.objects.filter(algorithm_version=versions[0])


def get_selected_metrics(params, metrics1, metrics2):
    selected_metrics1 = get_metrics_by_id(params, "metrics1_id", metrics1)
    selected_metrics2 = get_metrics_by_id(params, "metrics2_id", metrics2)
    return (selected_metrics1, selected_metrics2)


def get_metrics_by_id(params, param_key, metrics):
    metric_id = params[param_key]
    if metric_id and any(metric.pk == metric_id for metric in metrics):
        return Metrics.objects.get(pk=metric_id)

    if len(metrics) > 0:
        params[param_key] = metrics[0].pk
        return metrics[0]
    return None


def get_selected_molecule(params, common_molecules):
    if params["molecule_id"]:
        try:
            return Molecule.objects.get(pk=params["molecule_id"])
        except Molecule.DoesNotExist:
            return None

    elif len(common_molecules) > 0:
        selected_molecule = common_molecules[0]
        params["molecule_id"] = selected_molecule.pk
        return selected_molecule


def get_algo_data(a1, a2, metrics1, metrics2):
    return [["Algorithm comparison", a1.name, a2.name],
            ["gate_depth", metrics1.gate_depth, metrics2.gate_depth],
            ["qubit_count", metrics1.qubit_count, metrics2.qubit_count],
            ["average_iterations", metrics1.average_iterations,
            metrics2.average_iterations],
            ["success_rate", metrics1.success_rate, metrics2.success_rate]]


def compare_algorithms(request, a1_id, a2_id):
    algorithms = Algorithm.objects.filter(pk=a1_id) | Algorithm.objects.filter(pk=a2_id)
    if len(algorithms) != 2:  # check that we have found two unique algorithms
        return redirect("home")

    (a1, a2) = algorithms
    if ((not a1.public and request.user.pk != a1.user.pk) or
       (not a2.public and request.user.pk != a2.user.pk)):
        raise PermissionDenied

    (versions1, versions2) = (get_versions(a1), get_versions(a2))
    params = get_comparison_view_params(request)
    (metrics1, metrics2) = get_metrics(params, versions1, versions2)
    (selected_metrics1, selected_metrics2) = get_selected_metrics(params, metrics1, metrics2)
    (av1, av2) = get_selected_versions(params, versions1, versions2)
    common_molecules = get_common_molecules(versions1, versions2)
    selected_molecule = get_selected_molecule(params, common_molecules)
    graph_data = [[0, 0, 0], [1, 2, 4], [2, 4, 8], [3, 6, 10], [4, 6, 10]]
    algo_data = get_algo_data(a1, a2, selected_metrics1, selected_metrics2)


    return render(request, 'WebCLI/compareAlgorithms.html',
                  {'params': params, 'a1': a1, 'av1': av1, 'a2': a2, 'av2': av2,
                   'metrics1': metrics1, 'metrics2': metrics2,
                   'selected_metrics1': selected_metrics1, 'selected_metrics2': selected_metrics2,
                   'common_molecules': common_molecules, 'molecule': selected_molecule,
                   'versions1': versions1, 'versions2': versions2,
                   'graph_data': graph_data, 'algo_data': algo_data})
