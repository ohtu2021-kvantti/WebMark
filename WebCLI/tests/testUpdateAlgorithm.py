from ddf import M, N
from django.contrib.auth.models import User
from django.test import Client, TestCase
from ..models import Algorithm_type, Algorithm

class TestUpdateAlgorithm(TestCase):

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
             {'username': self.test_user.username, 'password': self.test_user.password}
        )
        self.client.post('/newAlgorithmType/',
               {'type_name': 'type1'}
        )
        self.client.post('/newAlgorithm/',
               {'user': self.test_user.username,
                'name': 'test_algorithm',
                'algorithm_type': Algorithm_type.objects.get(type_name='type1').pk,
                'public': 'on',
                'article_link': 'https://kela.fi',
                'github_link': 'https://vn.fi',
                'algorithm': 'Very nice algorithm',
                'circuit': 'circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))\nX(target=(3,))',
                'optimizer_module': 'scipy',
                'optimizer_method': 'BFGS'}
        )

    def test_update_details(self):
        a = Algorithm.objects.get(name='test_algorithm')
        self.client.post('/updateAlgorithm/?index='+str(a.pk),
                    {'name': 'test_algorithm',
                     'algorithm_type': Algorithm_type.objects.get(type_name='type1').pk,
                     'public': 'on',
                     'article_link': 'https://aalink1.com',
                     'github_link': 'https://gtlink1.com',
                     'user': User.objects.get(username=self.test_user.username).pk})
        a = Algorithm.objects.get(name='test_algorithm')
        self.assertEqual(a.article_link, 'https://aalink1.com')