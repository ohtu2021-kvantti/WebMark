from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput
from django.forms.widgets import NumberInput, TextInput
from .models import Algorithm, Molecule, Algorithm_type, Algorithm_version, Metrics
import quantmark as qm


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user', 'name', 'algorithm_type', 'public',
                  'article_link', 'github_link']
        widgets = {
            'name': TextInput(),
            'user': HiddenInput(),
        }


class AlgorithmTypeForm(ModelForm):
    class Meta:
        model = Algorithm_type
        fields = ['type_name']
        widgets = {
            'type_name': TextInput(),
        }


class AlgorithmVersionForm(ModelForm):
    def clean_circuit(self):
        circuit = self.clean().get('circuit')
        if not qm.circuit.validate_circuit_syntax(circuit):
            self.add_error('circuit', 'use string printed by tequila.circuit')
        return circuit

    class Meta:
        model = Algorithm_version
        fields = ['algorithm', 'circuit', 'optimizer_module',
                  'optimizer_method', 'timestamp', 'algorithm_id']
        widgets = {
            'timestamp': HiddenInput(),
            'algorithm_id': HiddenInput(),
            'algorithm': Textarea(attrs={'rows': 6}),
            'circuit': Textarea(attrs={'rows': 10}),
            'optimizer_method': TextInput(),
            'optimizer_module': TextInput(),
        }
        labels = {
            'algorithm': 'Description',
        }


class MetricsForm(ModelForm):
    class Meta:
        model = Metrics
        fields = ['algorithm_version', 'molecule', 'iterations',
                  'measurements', 'circuit_depth', 'accuracy']
        widgets = {
            'algorithm_version': HiddenInput(),
            'iterations': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'measurements': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'circuit_depth': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'accuracy': NumberInput(attrs={'min': 0, 'max': 1000000}),
        }


class MoleculeForm(ModelForm):

    def clean_structure(self):
        structure = self.clean().get('structure')
        if not qm.molecule.validate_geometry_syntax(structure):
            self.add_error('structure', 'Atom syntax (one atom per line): Li 0.0 0.0 1.6')
        return structure

    def clean_active_orbitals(self):
        active_orbitals = self.clean().get('active_orbitals')
        if not qm.molecule.validate_orbitals_syntax(active_orbitals):
            self.add_error('active_orbitals', 'Orbital syntax (one orbital per line): A1 1 2 4 5 7')
        return active_orbitals

    class Meta:
        model = Molecule
        fields = ['name', 'structure', 'active_orbitals', 'basis_set', 'transformation']
        labels = {
            'structure': 'Geometry'
        }
        widgets = {
            'name': TextInput(),
            'basis_set': TextInput(),
            'transformation': TextInput(),
            'structure': Textarea(attrs={'rows': 6, 'cols': 50}),
            'active_orbitals': Textarea(attrs={'rows': 6, 'cols': 50}),
        }


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
