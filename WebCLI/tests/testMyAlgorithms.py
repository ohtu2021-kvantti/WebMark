from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Algorithm_type, Algorithm
from ..models import Algorithm_version
import datetime
import pytz


class TestNewAlgorithm(TestCase):

    @classmethod
    def setUpTestAlgorithms(self):
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

    def setUpTestAlgorithmVersions(self):
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

    @classmethod
    def setUpTestData(self):
        self.u1 = User.objects.create_user('Bob', 'bob@example.com', 'bobpassword')
        self.u1.save()
        self.u2 = User.objects.create_user('Alice', 'alice@example.com', 'alicepassword')
        self.u2.save()
        self.types = []
        for i in range(3):
            at = Algorithm_type(type_name='type'+str(i+1))
            at.save()
            self.types.append(at)
        self.setUpTestAlgorithms()
        self.setUpTestAlgorithmVersions(self)

    def setUp(self):
        self.client.login(username="Bob", password="bobpassword")

    def test_my_algorithms_view(self):
        response = str(self.client.get("/myAlgorithms/").content)
        self.assertFalse(response.find('Algo1') < 0)
        self.assertFalse(response.find('Algo2') < 0)
        self.assertFalse(response.find('Algo3') < 0)
        self.assertTrue(response.find('Algo4') < 0)
        self.assertTrue(response.find('Algo5') < 0)
        self.assertTrue(response.find('Algo6') < 0)
        self.assertFalse(response.find('https://alink1.com') < 0)
        self.assertFalse(response.find('https://gtlink1.com') < 0)
