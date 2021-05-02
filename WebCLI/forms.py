from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput, Select, ChoiceField
from django.forms.widgets import NumberInput, TextInput
from .models import Algorithm, Molecule, Algorithm_type, Algorithm_version, Metrics
import quantmark as qm
from .misc.analyze_options import optimizer_methods, optimizer_modules, basis_set_options
from .misc.helpers import get_transformation_options


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user', 'name', 'algorithm_type', 'public',
                  'article_link', 'github_link']
        widgets = {
            'name': TextInput(),
            'user': HiddenInput(),
            'article_link': TextInput(attrs={'placeholder': 'e.g. https://www.nature.com/article'}),
            'github_link': TextInput(attrs={'placeholder': 'e.g. https://www.github.com/u/repo'}),

        }


class AlgorithmTypeForm(ModelForm):
    class Meta:
        model = Algorithm_type
        fields = ['type_name']
        widgets = {
            'type_name': TextInput(),
        }


class AlgorithmVersionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            module = kwargs['initial']['optimizer_module']
        else:
            module = args[0].get('optimizer_module')
        methods = optimizer_methods(module)
        self.fields['optimizer_method'] = ChoiceField(choices=((x, x) for x in methods))

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
            'algorithm': Textarea(attrs={'rows': 6,
                                         'placeholder': 'Pseudocode, for example.'}),
            'circuit': Textarea(attrs={'rows': 10,
                                       'placeholder': 'e.g. Ry(target=(0,), parameter=a)'}),
            'optimizer_module': Select(choices=((x, x) for x in optimizer_modules()),
                                       attrs={'class': 'form-control'}),
        }
        labels = {
            'algorithm': 'Description',
        }


class MetricsForm(ModelForm):
    class Meta:
        model = Metrics
        fields = ['algorithm_version', 'molecule', 'gate_depth',
                  'qubit_count', 'average_iterations', 'success_rate']
        widgets = {
            'algorithm_version': HiddenInput(),
            'gate_depth': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'qubit_count': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'averaget_iterations': NumberInput(attrs={'min': 0, 'max': 1000000}),
            'success_rate': NumberInput(attrs={'min': 0, 'max': 1000000}),
        }


class MoleculeForm(ModelForm):

    def clean_structure(self):
        structure = self.clean().get('structure')
        if not qm.molecule.validate_geometry_syntax(structure):
            self.add_error('structure', 'Atom syntax (one atom per line): Li 0.0 0.0 1.6')
        return structure

    def clean_active_orbitals(self):
        active_orbitals = self.clean().get('active_orbitals')
        if (active_orbitals == ''):
            return active_orbitals
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
            'basis_set': Select(choices=((x, x) for x in basis_set_options())),
            'transformation': Select(choices=((x, x) for x in get_transformation_options())),
            'structure': Textarea(attrs={'rows': 6, 'cols': 50,
                                         'placeholder': 'e.g. H 0.0 0.0 0.0\n\tLi 0.0 0.0 1.6'}),
            'active_orbitals': Textarea(attrs={'rows': 6, 'cols': 50,
                                               'placeholder': 'e.g. A1 1\n\tB1 0'}),
        }


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
