from .models import Algorithm, Algorithm_type, Molecule
from django.utils import timezone

def new_algorithm(user, algorithm_name, algorithm_type, algorithm, molecule, public):
    a = Algorithm.objects.create(user=user, name=algorithm_name, timestamp=timezone.now(), algorithm_type=algorithm_type, algorithm=algorithm, molecule=molecule, public=public)
    a.save()
    return a

def save_metrics(algorithm, iterations = None, measurements = None, circuit_depth = None, accuracy = None):
    if iterations!=None:
        algorithm.iterations = iterations
    if measurements!=None:
        algorithm.measurements = measurements
    if circuit_depth!=None:
        algorithm.circuit_depth = circuit_depth
    if accuracy!=None:
        algorithm.accuracy = accuracy
    algorithm.save()

def get_user_algorithms(user):
    return Algorithm.objects.filter(user=user)

def get_public_algorithms():
    return Algorithm.objects.filter(public=True)

def new_molecule(name, structure):
    m  = Molecule.objects.create(name=name, structure=structure)
    m.save()
    return m

def get_molecules():
    return Molecule.objects.all()

def new_algorithm_type(name):
    at = Algorithm_type.objects.create(type_name=name)
    at.save()
    return at

def get_algorithm_types():
    return Algorithm_type.objects.all()
