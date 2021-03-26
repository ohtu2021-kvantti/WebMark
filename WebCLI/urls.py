# pages/urls.py
from django.urls import path
<<<<<<< HEAD
from .views import new_algorithm, algorithm_details_view, new_algorithm_type
from .views import new_molecule, AlgorithmListView, add_metrics, view_molecule
from .views import MyAlgorithmListView, add_version, compare_algorithms, update_algorithm
from .views.forms import SignUpView
=======
from .views.new_algorithm import new_algorithm
from .views.new_molecule import new_molecule
from .views.new_algorithm_type import new_algorithm_type
from .views.add_metrics import add_metrics
from .views.view_molecule.view_molecule
from .views.new_version import add_version
from .views.update_algorithm import update_algorithm
from .views.compare_algorithms import compare_algorithms
from .views.algorithm_details_view import algorithm_details_view
from .views.homepage import AlgorithmListView
from .views.my_algorithms import MyAlgorithmListView
from .forms import SignUpView
>>>>>>> main

urlpatterns = [
    path('', AlgorithmListView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('newAlgorithm/', new_algorithm, name='newAlgorithm'),
    path('newMolecule/', new_molecule, name='newMolecule'),
    path('newAlgorithmType/', new_algorithm_type, name='newAlgorithmType'),
    path('algorithm/<int:algorithm_id>', algorithm_details_view, name='algorithm_details'),
    path('addMetrics/', add_metrics, name='add_metrics'),
    path('myAlgorithms/', MyAlgorithmListView.as_view(), name="myAlgorithms"),
    path('compare/<int:a1_id>/<int:a2_id>', compare_algorithms, name="compare_algorithms"),
    path('addVersion/', add_version, name='add_version'),
    path('updateAlgorithm/', update_algorithm, name='updateAlgorithm'),
    path('molecule/', view_molecule, name='viewMolecule'),
]
