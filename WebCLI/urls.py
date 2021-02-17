"""WebMark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# pages/urls.py
from django.urls import path
from .views import new_algorithm, algorithm_details_view, new_algorithm_type
from .views import new_molecule, SignUpView, AlgorithmListView, add_metrics
from .views import MyAlgorithmListView, add_version

urlpatterns = [
    path('', AlgorithmListView.as_view(), name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('newAlgorithm/', new_algorithm, name='newAlgorithm'),
    path('newMolecule/', new_molecule, name='newMolecule'),
    path('newAlgorithmType/', new_algorithm_type, name='newAlgorithmType'),
    path('algorithm/<algorithm_id>', algorithm_details_view, name='algorithm_details'),
    path('addMetrics/', add_metrics, name='add_metrics'),
    path('addVersion/', add_version, name='add_version'),
    path('myAlgorithms/', MyAlgorithmListView.as_view(), name="myAlgorithms")
]
