from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Algorithm_type(models.Model):
    type_name = models.TextField()

    def __str__(self):
        return self.type_name


class Molecule(models.Model):
    name = models.TextField()
    structure = models.TextField()
    active_orbitals = models.TextField(blank=True, default="")
    basis_set = models.TextField(default="")
    transformation = models.TextField(blank=True, default="")

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('viewMolecule', args=[str(self.pk)])

    def __str__(self):
        return self.name


class Algorithm(models.Model):
    name = models.TextField()
    public = models.BooleanField()
    algorithm_type = models.ForeignKey(Algorithm_type, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article_link = models.URLField(blank=True)
    github_link = models.URLField(blank=True)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('algorithm_details', args=[str(self.pk)])

    def __str__(self):
        return self.name


class Algorithm_version(models.Model):
    algorithm_id = models.ForeignKey(Algorithm, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    algorithm = models.TextField()
    circuit = models.TextField(default="")
    optimizer_module = models.TextField(blank=True)
    optimizer_method = models.TextField(blank=True)

    def __str__(self):
        return str(self.timestamp)


class Metrics(models.Model):
    algorithm_version = models.ForeignKey(Algorithm_version, on_delete=models.CASCADE)
    molecule = models.ForeignKey(Molecule, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    measurements = models.IntegerField(null=True, blank=True)
    last_analyze_ok = models.BooleanField(default=False)
    in_analyze_queue = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now)
    qubit_count = models.IntegerField(null=True, blank=True)
    gate_depth = models.IntegerField(null=True, blank=True)
    average_iterations = models.FloatField(null=True, blank=True)
    success_rate = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.molecule.name


class Average_history(models.Model):
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    data = models.FloatField(null=True, blank=True)
    iteration_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.iteration_number}:{self.data}'


class Accuracy_history(models.Model):
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    data = models.FloatField(null=True, blank=True)
    iteration_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.iteration_number}:{self.data}'
