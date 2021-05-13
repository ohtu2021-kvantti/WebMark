from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied

from .AlgorithmViewBase import AlgorithmViewBase
from ..models import Algorithm, Molecule, Metrics
from WebCLI.models import Accuracy_history, Average_history


class AlgorithmComparisonView(AlgorithmViewBase):

    def _get_selected_versions(self, params, versions1, versions2):
        version1 = self.get_selected_version(params["version1_id"], versions1)
        version2 = self.get_selected_version(params["version2_id"], versions2)
        return version1, version2

    def _get_all_metrics(self, params, versions1, versions2):
        metrics1 = self.get_metrics(params["version1_id"], versions1)
        metrics2 = self.get_metrics(params["version2_id"], versions2)
        return metrics1, metrics2

    def _get_all_selected_metrics(self, params, metrics1, metrics2):
        selected_metrics1 = self.get_selected_metrics(params["metrics1_id"], metrics1)
        selected_metrics2 = self.get_selected_metrics(params["metrics2_id"], metrics2)
        return [selected_metrics1, selected_metrics2]

    def _get_common_molecules(self, versions):
        molecules1 = Metrics.objects.filter(algorithm_version=versions[0]).values("molecule")
        molecules2 = Metrics.objects.filter(algorithm_version=versions[1]).values("molecule")
        common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))
        return common_molecules

    def _get_selected_molecule(self, params, common_molecules):
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

    def _update_params(self, params, selected_metrics_list, selected_versions):
        params["metrics1_id"] = selected_metrics_list[0].pk if selected_metrics_list[0] else None
        params["metrics2_id"] = selected_metrics_list[1].pk if selected_metrics_list[1] else None
        params["version1_id"] = selected_versions[0].pk if selected_versions[0] else None
        params["version2_id"] = selected_versions[1].pk if selected_versions[1] else None

    def get(self, request, a1_id, a2_id):
        algorithms = Algorithm.objects.filter(pk=a1_id) | Algorithm.objects.filter(pk=a2_id)
        if len(algorithms) != 2:  # check that we have found two unique algorithms
            return redirect("home")

        (a1, a2) = algorithms
        if ((not a1.public and request.user.pk != a1.user.pk) or
                (not a2.public and request.user.pk != a2.user.pk)):
            raise PermissionDenied

        (versions1, versions2) = (
            self.get_versions_with_version_number(a1),
            self.get_versions_with_version_number(a2)
        )
        params = self.get_params(
            request, ["version1_id", "metrics1_id", "version2_id", "metrics2_id", "molecule_id"]
        )
        (metrics1, metrics2) = self._get_all_metrics(params, versions1, versions2)
        selected_metrics_list = self._get_all_selected_metrics(params, metrics1, metrics2)
        selected_versions = self._get_selected_versions(params, versions1, versions2)
        common_molecules = self._get_common_molecules(selected_versions)
        self._update_params(params, selected_metrics_list, selected_versions)
        selected_molecule = self._get_selected_molecule(params, common_molecules)
        average_history_graph_data = self.get_history_graph_data(
            Average_history, selected_metrics_list
        )
        accuracy_history_graph_data = self.get_history_graph_data(
            Accuracy_history, selected_metrics_list
        )

        return render(request, 'WebCLI/compareAlgorithms.html',
                      {'params': params, 'a1': a1, 'av1': selected_versions[0],
                       'a2': a2, 'av2': selected_versions[1],
                       'metrics1': metrics1, 'metrics2': metrics2,
                       'selected_metrics1': selected_metrics_list[0],
                       'selected_metrics2': selected_metrics_list[1],
                       'common_molecules': common_molecules, 'molecule': selected_molecule,
                       'versions1': versions1, 'versions2': versions2,
                       'average_history_graph_data': average_history_graph_data,
                       'accuracy_history_graph_data': accuracy_history_graph_data})
