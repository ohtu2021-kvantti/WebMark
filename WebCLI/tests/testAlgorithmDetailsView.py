from django.test import TestCase
from ddf import G
from ..models import Molecule

class testAlgorithmDetailsView(TestCase):
    def test_ddf_hello_world(self):
        molecule = G(Molecule)
        molecules= Molecule.objects.filter(name=molecule.name).first()
        self.assertEquals(molecule.name, molecules.name)