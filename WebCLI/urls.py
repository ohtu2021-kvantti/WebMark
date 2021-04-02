# pages/urls.py
from django.urls import path
from .views.new_algorithm import new_algorithm
from .views.new_molecule import new_molecule
from .views.new_algorithm_type import new_algorithm_type
from .views.new_version import add_version
from .views.update_algorithm import update_algorithm
from .views.compare_algorithms import compare_algorithms
from .views.algorithm_details_view import algorithm_details_view
from .views.homepage import AlgorithmListView
from .views.my_algorithms import MyAlgorithmListView
from .forms import SignUpView

urlpatterns = [
    path('', AlgorithmListView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('newAlgorithm/', new_algorithm, name='newAlgorithm'),
    path('newMolecule/', new_molecule, name='newMolecule'),
    path('newAlgorithmType/', new_algorithm_type, name='newAlgorithmType'),
    path('algorithm/<int:algorithm_id>', algorithm_details_view, name='algorithm_details'),
    path('myAlgorithms/', MyAlgorithmListView.as_view(), name="myAlgorithms"),
    path('compare/<int:a1_id>/<int:a2_id>', compare_algorithms, name="compare_algorithms"),
    path('addVersion/', add_version, name='add_version'),
    path('updateAlgorithm/', update_algorithm, name='updateAlgorithm'),
]
