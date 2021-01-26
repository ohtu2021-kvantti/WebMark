from django.test import TestCase
from django.contrib.auth.models import User

from .db import new_algorithm, new_algorithm_type, new_molecule, get_public_algorithms, get_molecules, get_algorithm_types, save_metrics

class DatabaseTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        atype = new_algorithm_type('VQE')
        molecule = new_molecule('water', 'H2O')
        algorithm = new_algorithm(user, 'fast algo', atype, 'asfasd\nafsdfasdf\nwrwrewe\n', molecule, True)
        save_metrics(algorithm, 1, 2, 3, 4.04)

        atype = new_algorithm_type('VQE-simple')
        molecule = new_molecule('hydrogen', 'H2')
        algorithm = new_algorithm(user, 'super algo', atype, 'xxxd\nyyyydf\nczzzzzz\n', molecule, False)
        save_metrics(algorithm, 5, 6, 7, 8.08)

    def test_list_public_algorithms(self):
        a = get_public_algorithms()
        self.assertEqual(len(a), 1)
        self.assertEqual(a[0].accuracy, 4.04)
        self.assertEqual(a[0].molecule.name, 'water')
        self.assertEqual(a[0].molecule.structure, 'H2O')
        self.assertEqual(a[0].algorithm_type.type_name, 'VQE')
        self.assertEqual(a[0].user.username, 'john')
        self.assertEqual(a[0].name, 'fast algo')

    def test_list_molecules(self):
        m = get_molecules()
        self.assertEqual(len(m), 2)

    def test_list_types(self):
        at = get_algorithm_types()
        self.assertEqual(len(at), 2)