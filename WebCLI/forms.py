from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
from django.forms import ModelForm, Textarea, HiddenInput, Form
from django.forms import CharField
from django.forms.widgets import NumberInput
from .models import Algorithm, Molecule, Algorithm_type, Metrics


class AlgorithmForm(ModelForm):
    class Meta:
        model = Algorithm
        fields = ['user', 'name', 'algorithm_type', 'public',
                  'article_link', 'github_link']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
            'user': HiddenInput(),
        }


class AlgorithmTypeForm(ModelForm):
    class Meta:
        model = Algorithm_type
        fields = ['type_name']
        widgets = {
            'type_name': Textarea(attrs={'rows': 1, 'cols': 50}),
        }


class AlgorithmVersionForm(Form):
    algorithm = CharField(widget=Textarea)


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
    class Meta:
        model = Molecule
        fields = ['name', 'structure']
        widgets = {
            'name': Textarea(attrs={'rows': 1, 'cols': 50}),
        }


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'
