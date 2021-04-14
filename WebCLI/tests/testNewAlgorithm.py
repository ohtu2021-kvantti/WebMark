from ddf import M, N
from django.contrib.auth.models import User
from django.test import Client, TestCase
from ..models import Molecule
from ..models import Molecule, Algorithm_type, Algorithm, Algorithm_version

class TestNewAlgorithm(TestCase):

    def setUp(self):
        self.client = Client()
        self.test_user = N(User, username=M(r'________'), password=M(r'________'))
        self.client.post(
            '/signup/',
            {'username': self.test_user.username,
             'password1': self.test_user.password, 'password2': self.test_user.password}
        )
        self.client.post(
             '/accounts/login/',
             {'username': self.test_user.username, 'password': self.test_user.password})

    def test_add_algorithm_with_2_versions(self):
        user_id = User.objects.get(username=self.test_user).pk
        self.client.post('/newAlgorithmType/',
                    {'type_name': 'VQE'})
        self.client.post('/newAlgorithm/',
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
        self.client.post('/addVersion/?index='+str(a.pk),
                    {'algorithm': 'Other nice algorithm',
                     'circuit': 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(3,))',
                     'optimizer_module': 'scipy',
                     'optimizer_method': 'BFGS',
                     'timestamp': '2021-03-29 13:53:06.581346',
                     'algorithm_id': str(a.pk)})
        v = Algorithm_version.objects.filter(algorithm_id=a)

        self.assertEqual(a.public, True)
        self.assertEqual(a.algorithm_type.type_name, 'VQE')
        self.assertEqual(a.user.username, self.test_user.username)
        self.assertEqual(len(v), 2)
        self.assertEqual(v[1].circuit, 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(3,))')

def test_add_algorithm_with_incorrect_circuit(self):
        user_id = User.objects.get(username='testuser3').pk
        self.c.post('/newAlgorithmType/',
                    {'type_name': 'VQE'})
        self.c.post('/newMolecule/',
                    {'name': 'Hydrogen', 'structure': 'H2'})
        self.c.post('/newAlgorithm/',
                    {'user': self.test_user.username,
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