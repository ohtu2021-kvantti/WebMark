from typing import List, Optional, Type, Dict
from django.shortcuts import redirect, render
from django.core.exceptions import PermissionDenied
from .AlgorithmViewBase import AlgorithmViewBase
from ..models import Algorithm, Molecule, Metrics, Accuracy_history, Average_history
from ..models import Algorithm_version
from django.db.models import F


def get_selected_molecule(
        params: Dict,
        molecules_with_metrics) -> Optional[Type[Molecule]]:
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


def get_metrics_graph_data(selected_molecule, algorithm) -> List[List]:
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


class AlgorithmDetailsView(AlgorithmViewBase):

    def get(self, request, algorithm_id):
        try:
            algorithm = Algorithm.objects.get(pk=algorithm_id)
        except Algorithm.DoesNotExist:
            return redirect("home")

        if not algorithm.public and request.user.pk != algorithm.user.pk:
            raise PermissionDenied

        versions = self.get_versions_with_version_number(algorithm)
        params = self.get_params(request, ["version_id", "metrics_id", "molecule_id"])
        metrics = self.get_metrics(params["version_id"], versions)
        selected_metrics = self.get_selected_metrics(params["metrics_id"], metrics)
        params["metrics_id"] = selected_metrics.pk if selected_metrics else None
        selected_version = self.get_selected_version(params["version_id"], versions)
        params["version_id"] = selected_version.pk if selected_version else None
        molecules_with_metrics = get_molecules_with_metrics(versions)
        selected_molecule = get_selected_molecule(params, molecules_with_metrics)
        metrics_graph_data = get_metrics_graph_data(selected_molecule, algorithm)
        molecules = Molecule.objects.all()

        accuracy_history = self.get_history_graph_data(Accuracy_history, [selected_metrics])
        average_history = self.get_history_graph_data(Average_history, [selected_metrics])

        data = {'algorithm': algorithm, 'versions': versions, 'params': params,
                'metrics_graph_data': metrics_graph_data, 'metrics': metrics,
                'molecules_with_metrics': molecules_with_metrics,
                'selected_version': selected_version,
                'selected_metrics': selected_metrics,
                'selected_molecule': selected_molecule,
                'molecules': molecules,
                'accuracy_history_graph_data': accuracy_history,
                'average_history_graph_data': average_history}

        return render(request, 'WebCLI/algorithm.html', data)


def in_analysis(request):
    module = request.GET.get('version_id')
    av = Algorithm_version.objects.get(pk=module)
    metrics = Metrics.objects.filter(algorithm_version=av, in_analyze_queue=True)
    molecules = []
    for m in metrics:
        if m.molecule.name not in molecules:
            molecules.append(m.molecule.name)
    return render(request, 'WebCLI/in_analysis.html', {'molecules': molecules})


def refresh_metrics(request):
    metrics_id = request.GET.get('version_id')
    molecule_id = request.GET.get('molecule_id')
    metrics = Metrics.objects.get(algorithm_version=metrics_id, molecule=molecule_id)
    return render(request, 'WebCLI/metrics.html', {'metrics': metrics})
