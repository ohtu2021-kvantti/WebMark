from django.test import SimpleTestCase, TestCase, Client
from django.contrib.auth.models import User

from .db import new_algorithm, new_algorithm_type, new_molecule, save_metrics
from .db import get_algorithm_types, get_molecules, get_public_algorithms
from django.urls import reverse


class DatabaseTest(TestCase):
    def setUp(self):
        user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        atype = new_algorithm_type('VQE')
        molecule = new_molecule('water', 'H2O')
        algorithm = new_algorithm(user, 'fast algo', atype, 'asfasd\nafasdf\nwre\n', molecule, True)
        save_metrics(algorithm, 1, 2, 3, 4.04)

        atype = new_algorithm_type('VQE-simple')
        molecule = new_molecule('hydrogen', 'H2')
        algorithm = new_algorithm(user, 'super algo', atype, 'xxxd\nyydf\nzzzz\n', molecule, False)
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


class WebFunctionTest(TestCase):

    def test_signup(self):
        c = Client()
        response = c.post(
            '/signup/',
            {'username': 'testuser1', 'password1': 'sekred010', 'password2': 'sekred010'}
        )
        self.assertEqual(response.status_code, 302)

    def test_login(self):
        c = Client()
        response = c.post(
            '/signup/',
            {'username': 'testuser2', 'password1': 'sekred010', 'password2': 'sekred010'}
        )
        response = c.login(username='testuser2', password='sekred010')
        self.assertEqual(response, True)


"""
    def test_authorized_content_unseen(self):
        c = Client()
        c.post('/newMolecule/', {'name': 'test_molecule', 'structure': 'test_structure'})
        c.post('/newAlgorithmType/', {'type_name': 'test_type'})
        c.post('/newAlgorithm',
           {'name': 'test_algorithm', 'algorithm_type': 1,
            'molecule': 1, 'public': True, 'algorithm': 'exec()',
            'article_link': 'https://kela.fi', 'github_link': 'https://kela.fi'}
        )
        response = c.get('/algorithm/?index=1')
        self.assertEqual(response.status_code, 403)
"""


class AlgorithmComparisonTest(SimpleTestCase):

    def setUp(self):
        user = User.objects.create_user("testuser", "test@example.com", "secret")
        self.client.login(username="testuser", password="testuserpassword")
        other_user = User.objects.create_user("otheruser", "other@example.com", "secret")
        algorithm_type = new_algorithm_type("VQE")
        molecule = new_molecule("water", "H2O")
        self.my_algorithm = new_algorithm(
            user, "my algo", algorithm_type, "execute()", molecule, public=True
        )
        self.my_private_algorithm = new_algorithm(
            user, "my private algo", algorithm_type, "execute()", molecule, public=False
        )
        self.other_user_private_algorithm = new_algorithm(
            other_user, "private algo", algorithm_type, "exec()", molecule, public=False
        )
        self.other_user_public_algorithm = new_algorithm(
            other_user, "public algo", algorithm_type, "exec()", molecule, public=True
        )

    def random_parameters_are_handled_correctly(self):
        response = self.client.get("/compare/a/exec()")
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

    def cannot_compare_nonexistent_algorithms(self):
        response = self.client.get("/compare/10/11")
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

    def cannot_compare_algorithm_to_itself(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.my_algorithm.pk}"
        )
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

    def can_compare_to_private_by_current_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.my_private_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 200)

    def cannot_compare_to_private_algorithm_by_other_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.other_user_private_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 403)

    def can_compare_to_public_algorithm_by_other_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.other_user_public_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 200)
