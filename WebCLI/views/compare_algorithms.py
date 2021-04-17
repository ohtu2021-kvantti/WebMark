from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Algorithm, Molecule, Metrics
from WebCLI.misc.helpers import get_metrics, get_selected_version
from WebCLI.misc.helpers import get_selected_metrics, get_versions, to_positive_int_or_none
from WebCLI.models import Accuracy_history, Average_history
import itertools


def get_comparison_view_params(request):
    keys = ["version1_id", "metrics1_id", "version2_id", "metrics2_id", "molecule_id"]
    return {k: to_positive_int_or_none(request.GET.get(k)) for k in keys}


def get_selected_versions(params, versions1, versions2):
    version1 = get_selected_version(params, "version1_id", versions1)
    version2 = get_selected_version(params, "version2_id", versions2)
    return (version1, version2)


def get_common_molecules(version1, version2):
    molecules1 = Metrics.objects.filter(algorithm_version=version1).values("molecule")
    molecules2 = Metrics.objects.filter(algorithm_version=version2).values("molecule")
    common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))
    return common_molecules


def get_all_metrics(params, versions1, versions2):
    metrics1 = get_metrics(params["version1_id"], versions1)
    metrics2 = get_metrics(params["version2_id"], versions2)
    return (metrics1, metrics2)


def get_all_selected_metrics(params, metrics1, metrics2):
    selected_metrics1 = get_selected_metrics(params, "metrics1_id", metrics1)
    selected_metrics2 = get_selected_metrics(params, "metrics2_id", metrics2)
    return (selected_metrics1, selected_metrics2)


def get_selected_molecule(params, common_molecules):
    if len(common_molecules) == 0:
        params["molecule_id"] = None
        return None
    if params["molecule_id"]:
        try:
            return Molecule.objects.get(pk=params["molecule_id"])
        except Molecule.DoesNotExist:
            return None
    selected_molecule = common_molecules[0]
    params["molecule_id"] = selected_molecule.pk
    return selected_molecule


def get_history_graph_data(HistoryModel, selected_metrics1, selected_metrics2):
    if selected_metrics1 and selected_metrics2:
        history_data1 = HistoryModel.objects.values_list("data", flat=True)
        history_data1 = history_data1.filter(analyzed_results=selected_metrics1)
        history_data2 = HistoryModel.objects.values_list("data", flat=True)
        history_data2 = history_data2.filter(analyzed_results=selected_metrics2)
        return histories_to_graph_data(history_data1, history_data2)
    return []


def histories_to_graph_data(history_data1, history_data2):
    graph_data_length = max(len(history_data1), len(history_data2))
    iterations = list(range(1, graph_data_length+1))
    return list(itertools.zip_longest(iterations, history_data1, history_data2))


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
    (metrics1, metrics2) = get_all_metrics(params, versions1, versions2)
    (selected_metrics1, selected_metrics2) = get_all_selected_metrics(params, metrics1, metrics2)
    (av1, av2) = get_selected_versions(params, versions1, versions2)
    common_molecules = get_common_molecules(av1, av2)
    selected_molecule = get_selected_molecule(params, common_molecules)
    average_history_graph_data = get_history_graph_data(
        Average_history, selected_metrics1, selected_metrics2
    )
    accuracy_history_graph_data = get_history_graph_data(
        Accuracy_history, selected_metrics1, selected_metrics2
    )

    return render(request, 'WebCLI/compareAlgorithms.html',
                  {'params': params, 'a1': a1, 'av1': av1, 'a2': a2, 'av2': av2,
                   'metrics1': metrics1, 'metrics2': metrics2,
                   'selected_metrics1': selected_metrics1, 'selected_metrics2': selected_metrics2,
                   'common_molecules': common_molecules, 'molecule': selected_molecule,
                   'versions1': versions1, 'versions2': versions2,
                   'average_history_graph_data': average_history_graph_data,
                   'accuracy_history_graph_data': accuracy_history_graph_data})
