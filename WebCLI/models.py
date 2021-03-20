from django.db import models
from django.contrib.auth.models import User


class Algorithm_type(models.Model):
    type_name = models.TextField()

    def __str__(self):
        return self.type_name


class Molecule(models.Model):
    name = models.TextField()
    structure = models.TextField()
    active_orbitals = models.TextField()
    basis_set = models.TextField()
    transformation = models.TextField()

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
    circuit = models.TextField()
    optimizer_module = models.TextField(null=True, blank=True)
    optimizer_method = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.timestamp)


class Metrics(models.Model):
    algorithm_version = models.ForeignKey(Algorithm_version, on_delete=models.CASCADE)
    molecule = models.ForeignKey(Molecule, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    iterations = models.IntegerField(null=True, blank=True)
    measurements = models.IntegerField(null=True, blank=True)
    circuit_depth = models.IntegerField(null=True, blank=True)
    accuracy = models.FloatField(null=True, blank=True)
    in_analyzed_queue = models.BooleanField(default=False)
    last_analyze_ok = models.BooleanField(default=False)

    def __str__(self):
        return self.molecule.name


class Analyzed_results(models.Model):
    metrics = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    qubit_count = models.IntegerField(null=True, blank=True)
    gate_depth = models.IntegerField(null=True, blank=True)
    average_iterations = models.FloatField(null=True, blank=True)
    success_rate = models.FloatField(null=True, blank=True)


class Average_history(models.Model):
    analyzed_results = models.ForeignKey(Analyzed_results, on_delete=models.CASCADE)
    data = models.FloatField(null=True, blank=True)
    iteration_number = models.IntegerField(null=True, blank=True)


class Accuracy_history(models.Model):
    analyzed_results = models.ForeignKey(Analyzed_results, on_delete=models.CASCADE)
    data = models.FloatField(null=True, blank=True)
    iteration_number = models.IntegerField(null=True, blank=True)
