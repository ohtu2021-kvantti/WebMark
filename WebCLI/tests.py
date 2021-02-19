from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Molecule, Algorithm_type, Algorithm, Algorithm_version


class WebFunctionTestLogin(TestCase):
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


class WebFunctionTestAddDataAsUser(TestCase):
    @classmethod
    def setUpClass(cls):
        c = Client()
        c.post('/signup/',
               {'username': 'testuser3', 'password1': 'sekred010', 'password2': 'sekred010'})

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
                    {'name': 'Lithium hydride', 'structure': 'LiH'})
        result = Molecule.objects.get(name='Lithium hydride')
        self.assertIsNotNone(result)

    def test_add_type(self):
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE (UCCSD)'})
        result = Algorithm_type.objects.get(type_name='VQE (UCCSD)')
        self.assertIsNotNone(result)

    def test_add_algorithm_with_2_versions(self):
        user_id = User.objects.get(username='testuser3').pk
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE'})
        self.c.post('/newMolecule/',
                    {'name': 'Hydrogen', 'structure': 'H2'})
        self.c.post('/newAlgorithm/',
                    {'user': user_id,
                     'name': 'test_algorithm',
                     'algorithm_type': Algorithm_type.objects.get(type_name='VQE').pk,
                     'molecule': Molecule.objects.get(name='Hydrogen').pk,
                     'public': 'on',
                     'algorithm': 'exec()',
                     'article_link': 'https://kela.fi',
                     'github_link': 'https://vn.fi'})
        self.c.post('/addVersion/?index='+str(user_id),
                    {'algorithm': 'print(1)\nexec()'})
        a = Algorithm.objects.get(name='test_algorithm')
        v = Algorithm_version.objects.filter(algorithm_id=a)

        self.assertEqual(a.public, True)
        self.assertEqual(a.algorithm_type.type_name, 'VQE')
        self.assertEqual(a.user.username, 'testuser3')
        self.assertEqual(a.molecule.name, 'Hydrogen')
        self.assertEqual(len(v), 2)
        self.assertEqual(v[1].algorithm, 'print(1)\nexec()')


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


class WebFunctionTestMyAlgorithmsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("testuser", "test@example.com", "secret")

    def setUp(self):
        self.client.login(username="testuser", password="secret")

    def test_my_algorithms_view(self):
        response = self.client.get("/myAlgorithms/")
        self.assertEqual(response.status_code, 200)
