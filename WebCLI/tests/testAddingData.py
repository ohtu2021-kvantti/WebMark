from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Molecule, Algorithm_type, Algorithm, Algorithm_version


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
