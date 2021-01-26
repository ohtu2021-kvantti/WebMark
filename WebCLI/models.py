from django.db import models
from django.contrib.auth.models import User


class Algorithm_type(models.Model):
    type_name = models.TextField()


class Molecule(models.Model):
    name = models.TextField()
    structure = models.TextField()


class Algorithm(models.Model):
    name = models.TextField()
    timestamp = models.DateTimeField()
    public = models.BooleanField()
    molecule = models.ForeignKey(Molecule, on_delete=models.CASCADE)
    algorithm_type = models.ForeignKey(Algorithm_type, on_delete=models.CASCADE)
    algorithm = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    iterations = models.IntegerField(null=True)
    measurements = models.IntegerField(null=True)
    circuit_depth = models.IntegerField(null=True)
    accuracy = models.FloatField(null=True)
