from django.test import TestCase, Client
from django.contrib.auth.models import User
from ..models import Algorithm_type, Algorithm
from ..models import Algorithm_version
import datetime
import pytz


class TestUpdateAlgorithm(TestCase):
    @classmethod
    def setUpTestData(cls):
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

    def test_update_other_user_details(self):
        self.u1 = User.objects.create_user('Bob', 'bob@example.com', 'bobpassword')
        self.u1.save()
        self.u2 = User.objects.create_user('Alice', 'alice@example.com', 'alicepassword')
        self.u2.save()
        self.types = []
        for i in range(3):
            at = Algorithm_type(type_name='type'+str(i+1))
            at.save()
            self.types.append(at)
        self.client.login(username="Bob", password="bobpassword")
        self.algos = []
        for i in range(3):
            a = Algorithm(name='Algo'+str(i+1), public=(i % 2 == 0),
                          algorithm_type=self.types[i], user=self.u1,
                          article_link='https://alink'+str(i+1)+'.com',
                          github_link='https://gtlink'+str(i+1)+'.com')
            a.save()
            self.algos.append(a)

        for i in range(3):
            a = Algorithm(name='Algo'+str(i+4), public=(i % 2 == 0),
                          algorithm_type=self.types[i], user=self.u2,
                          article_link='https://alink'+str(i+4)+'.com',
                          github_link='https://gtlink'+str(i+4)+'.com')
            a.save()
            self.algos.append(a)
        for i in range(6):
            av = Algorithm_version(algorithm_id=self.algos[i],
                                   timestamp=datetime.datetime(2021, 2, 10, 10, 0, 0, 0, pytz.UTC),
                                   algorithm='algorithm'+str(i+1)+'\nversion1\n',
                                   circuit="circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))",
                                   optimizer_module='scipy',
                                   optimizer_method='BFGS')
            av.save()
            av = Algorithm_version(algorithm_id=self.algos[i],
                                   timestamp=datetime.datetime(2021, 2, 10, 11, 0, 0, 0, pytz.UTC),
                                   algorithm='algorithm'+str(i+1)+'\nversion2\n',
                                   circuit="circuit:\nRy(target=(0,), parameter=a)",
                                   optimizer_module='scipy',
                                   optimizer_method='BFGS')
            av.save()
        a = Algorithm.objects.get(name='Algo4')
        response = self.client.get('/updateAlgorithm/?index='+str(a.pk))
        self.assertEqual(response.status_code, 403)
