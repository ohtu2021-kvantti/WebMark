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
from .views import home_view, algorithm_view, algorithm_details_view, algorithm_type_view, molecule_view, SignUpView

urlpatterns = [
    path('', home_view, name='home'),
    path('signup/', SignUpView.as_view(), name='signup'),
    path('newAlgorithm/', algorithm_view, name='newAlgorithm'),
    path('newMolecule/', molecule_view, name='newMolecule'),
    path('newAlgorithmType/', algorithm_type_view, name='newAlgorithmType'),
    path('details/', algorithm_details_view, name='details?name={a.name}'),
]
