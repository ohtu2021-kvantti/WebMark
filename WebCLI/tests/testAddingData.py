from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Molecule, Algorithm_type, Algorithm, Algorithm_version
from unittest.mock import patch


class TestLogin(TestCase):
    def test_signup(self):
        c = Client()
        response = c.post(
            '/signup/',
            {'username': 'testuser1', 'password1': 'sekred010', 'password2': 'sekred010'}
        )
        self.assertEqual(response.status_code, 302)
        response = c.login(username='testuser1', password='sekred010')
        self.assertEqual(response, True)

    def test_login(self):
        c = Client()
        c.post(
            '/signup/',
            {'username': 'testuser2', 'password1': 'sekred010', 'password2': 'sekred010'}
        )
        c.post(
            '/accounts/login/',
            {'username': 'testuser2', 'password': 'sekred010'})
        response = str(c.get('/').content)
        self.assertFalse(response.find('logged in - testuser2') < 0)

    def test_logout(self):
        c = Client()
        c.post(
            '/signup/',
            {'username': 'testuser4', 'password1': 'sekred010', 'password2': 'sekred010'}
        )
        c.post(
            '/accounts/login/',
            {'username': 'testuser4', 'password': 'sekred010'})
        c.get('/accounts/logout/')
        response = str(c.get('/').content)
        self.assertTrue(response.find('logged in - testuser4') < 0)


class TestAddDataAsUser(TestCase):
    @classmethod
    def setUpClass(cls):
        c = Client()
        c.post('/signup/',
               {'username': 'testuser3', 'password1': 'sekred010', 'password2': 'sekred010'})
        user_id = User.objects.get(username='testuser3').pk
        c.post('/accounts/login/',
               {'username': 'testuser3', 'password': 'sekred010'})
        c.post('/newAlgorithmType/',
               {'type_name': 'type1'})
        c.post('/newAlgorithm/',
               {'user': user_id,
                'name': 'test_algorithm',
                'algorithm_type': Algorithm_type.objects.get(type_name='type1').pk,
                'public': 'on',
                'article_link': 'https://kela.fi',
                'github_link': 'https://vn.fi',
                'algorithm': 'Very nice algorithm',
                'circuit': 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))\nX(target=(3,))',
                'optimizer_module': 'scipy',
                'optimizer_method': 'BFGS'})
        c.get('/accounts/logout/')

    def setUp(self):
        self.c = Client()
        self.c.post('/accounts/login/',
                    {'username': 'testuser3', 'password': 'sekred010'})

    def tearDown(self):
        self.c.get('/accounts/logout/')

    @classmethod
    def tearDownClass(cls):
        pass

    def test_add_molecule(self):
        self.c.post('/newMolecule/',
                    {'name': 'Lithium hydride',
                     'structure': 'H 0.0 0.0 0.0\nLi 0.0 0.0 1.6',
                     'active_orbitals': 'A1 1 2 4 5 7',
                     'basis_set': 'sto-3g',
                     'transformation': 'Bravyi-Kitaev'})
        result = len(Molecule.objects.filter(name='Lithium hydride'))
        self.assertEqual(result, 1)

    def test_add_molecule_with_incorrect_structure(self):
        self.c.post('/newMolecule/',
                    {'name': 'Lithium hydride2',
                     'structure': 'H 0.0 0.0 0.0Li 0.0 0.0 1.6',
                     'active_orbitals': 'A1 1 2 4 5 7',
                     'basis_set': 'sto-3g',
                     'transformation': 'Bravyi-Kitaev'})
        result = len(Molecule.objects.filter(name='Lithium hydride2'))
        self.assertEqual(result, 0)

    def test_add_molecule_with_incorrect_orbitals(self):
        self.c.post('/newMolecule/',
                    {'name': 'Lithium hydride3',
                     'structure': 'H 0.0 0.0 0.0\nLi 0.0 0.0 1.6',
                     'active_orbitals': '1 2 4 5 7',
                     'basis_set': 'sto-3g',
                     'transformation': 'Bravyi-Kitaev'})
        result = len(Molecule.objects.filter(name='Lithium hydride3'))
        self.assertEqual(result, 0)

    def test_add_type(self):
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE (UCCSD)'})
        result = Algorithm_type.objects.get(type_name='VQE (UCCSD)')
        self.assertIsNotNone(result)

    @patch("WebCLI.views.celery_app.send_task")
    def test_add_algorithm_with_2_versions(self, send_task):
        user_id = User.objects.get(username='testuser3').pk
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE'})
        self.c.post('/newAlgorithm/',
                    {'user': user_id,
                     'name': 'algo_2021',
                     'algorithm_type': Algorithm_type.objects.get(type_name='VQE').pk,
                     'public': 'on',
                     'article_link': 'https://kela.fi',
                     'github_link': 'https://vn.fi',
                     'algorithm': 'Other nice algorithm',
                     'circuit': 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))',
                     'optimizer_module': 'scipy',
                     'optimizer_method': 'BFGS'})
        a = Algorithm.objects.get(name='algo_2021')
        self.c.post('/addVersion/?index='+str(a.pk),
                    {'algorithm': 'Other nice algorithm',
                     'circuit': 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(3,))',
                     'optimizer_module': 'scipy',
                     'optimizer_method': 'BFGS',
                     'timestamp': '2021-03-29 13:53:06.581346',
                     'algorithm_id': str(a.pk)})
        v = Algorithm_version.objects.filter(algorithm_id=a)

        self.assertEqual(a.public, True)
        self.assertEqual(a.algorithm_type.type_name, 'VQE')
        self.assertEqual(a.user.username, 'testuser3')
        self.assertEqual(len(v), 2)
        self.assertEqual(v[1].circuit, 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(3,))')

    def test_add_algorithm_with_incorrect_circuit(self):
        user_id = User.objects.get(username='testuser3').pk
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE'})
        self.c.post('/newMolecule/',
                    {'name': 'Hydrogen', 'structure': 'H2'})
        self.c.post('/newAlgorithm/',
                    {'user': user_id,
                     'name': 'algo_2022',
                     'algorithm_type': Algorithm_type.objects.get(type_name='VQE').pk,
                     'public': 'on',
                     'article_link': 'https://kela.fi',
                     'github_link': 'https://vn.fi',
                     'algorithm': 'Other nice algorithm',
                     'circuit': 'Ry(target=(0,), parameter=a)\nX(target=(2,))',
                     'optimizer_module': 'scipy',
                     'optimizer_method': 'BFGS'})
        a = Algorithm.objects.filter(name='algo_2022')
        self.assertEqual(len(a), 0)

    def test_update_details(self):
        a = Algorithm.objects.get(name='test_algorithm')
        self.c.post('/updateAlgorithm/?index='+str(a.pk),
                    {'name': 'test_algorithm',
                     'algorithm_type': Algorithm_type.objects.get(type_name='type1').pk,
                     'public': 'on',
                     'article_link': 'https://aalink1.com',
                     'github_link': 'https://gtlink1.com',
                     'user': User.objects.get(username='testuser3').pk})
        a = Algorithm.objects.get(name='test_algorithm')
        self.assertEqual(a.article_link, 'https://aalink1.com')
