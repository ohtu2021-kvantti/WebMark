from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from ..models import Algorithm, Molecule, Algorithm_version, Metrics


def compare_algorithms(request, a1_id, a2_id):

    queryset = Algorithm.objects.filter(pk=a1_id) | Algorithm.objects.filter(pk=a2_id)
    if len(queryset) != 2:  # check that we have found two unique algorithms
        return redirect("home")

    (versions1, versions2) = (
        Algorithm_version.objects.filter(algorithm_id=queryset[0]).order_by('-timestamp'),
        Algorithm_version.objects.filter(algorithm_id=queryset[1]).order_by('-timestamp')
    )

    (av1, av2) = (versions1[0], versions2[0])
    if request.method == "POST":
        av1_id = request.POST.get('item1_id')
        av2_id = request.POST.get('item2_id')
        av1 = Algorithm_version.objects.get(pk=request.POST.get('otherVersion'))
        av2 = Algorithm_version.objects.get(pk=request.POST.get('otherVersion'))
        if av1_id:
            av1 = Algorithm_version.objects.get(pk=av1_id)
        if av2_id:
            av2 = Algorithm_version.objects.get(pk=av2_id)

    molecules1 = Metrics.objects.filter(algorithm_version=av1).values('molecule')
    molecules2 = Metrics.objects.filter(algorithm_version=av2).values('molecule')
    common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))
    selected_molecule = None
    if len(common_molecules) > 0:
        selected_molecule = common_molecules[0]

    if request.method == "POST" and request.POST.get('item3_id'):
        selected_molecule = Molecule.objects.get(pk=request.POST.get('item3_id'))
        av1 = Algorithm_version.objects.get(pk=request.POST.get('version1'))
        av2 = Algorithm_version.objects.get(pk=request.POST.get('version2'))
        molecules1 = Metrics.objects.filter(algorithm_version=av1).values('molecule')
        molecules2 = Metrics.objects.filter(algorithm_version=av2).values('molecule')
        common_molecules = Molecule.objects.filter(pk__in=molecules1.intersection(molecules2))

    metrics1 = None
    metrics2 = None
    graph_data = None
    algo_data = None
    (a1, a2) = queryset
    if selected_molecule is not None:
        metrics1 = Metrics.objects.get(algorithm_version=av1, molecule=selected_molecule)
        metrics2 = Metrics.objects.get(algorithm_version=av2, molecule=selected_molecule)

        # dummy data
        graph_data = [[0, 0, 0], [1, 2, 4], [2, 4, 8], [3, 6, 10], [4, 6, 10]]
        algo_data = [["Algorithm comparison", a1.name, a2.name],
                     ["Iterations", metrics1.iterations, metrics2.iterations],
                     ["Measurements", metrics1.measurements, metrics2.measurements],
                     ["Circuit depth", metrics1.circuit_depth, metrics2.circuit_depth],
                     ["Accuracy", metrics1.accuracy, metrics2.accuracy]]

    if ((not a1.public and request.user.pk != a1.user.pk) or
       (not a2.public and request.user.pk != a2.user.pk)):
        raise PermissionDenied

    return render(request, 'WebCLI/compareAlgorithms.html',
                  {'a1': a1, 'av1': av1, 'a2': a2, 'av2': av2,
                   'metrics1': metrics1, 'metrics2': metrics2,
                   'common_molecules': common_molecules, 'molecule': selected_molecule,
                   'versions1': versions1, 'versions2': versions2,
                   'graph_data': graph_data, 'algo_data': algo_data})
