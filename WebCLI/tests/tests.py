from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Molecule, Algorithm_type, Algorithm, Algorithm_version, Metrics
from django.urls import reverse
from django.utils import timezone
import datetime
import pytz


class AlgorithmComparisonTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = User.objects.create_user("testuser", "test@example.com", "secret")
        other_user = User.objects.create_user("otheruser", "other@example.com", "secret")

        algorithm_type = Algorithm_type.objects.create(type_name="VQE")
        algorithm_type.save()

        molecule = Molecule.objects.create(name="water", structure="H2O")
        molecule.save()

        cls.my_algorithm = Algorithm.objects.create(
            user=user, name="my public algorithm",
            algorithm_type=algorithm_type, public=True
        )
        cls.my_private_algorithm = Algorithm.objects.create(
            user=user, name="my private algorithm",
            algorithm_type=algorithm_type, public=False
        )
        cls.other_user_public_algorithm = Algorithm.objects.create(
            user=other_user, name="other user public algorithm",
            algorithm_type=algorithm_type, public=True
        )
        cls.other_user_private_algorithm = Algorithm.objects.create(
            user=other_user, name="other user private algorithm",
            algorithm_type=algorithm_type, public=False
        )

        cls.my_algorithm.save()
        cls.my_private_algorithm.save()
        cls.other_user_private_algorithm.save()
        cls.other_user_public_algorithm.save()

        av1 = Algorithm_version(algorithm_id=cls.my_algorithm, timestamp=timezone.now(),
                                algorithm="execute()")
        av1.save()

        av2 = Algorithm_version(algorithm_id=cls.my_private_algorithm, timestamp=timezone.now(),
                                algorithm="execute()")
        av2.save()

        av3 = Algorithm_version(algorithm_id=cls.other_user_private_algorithm,
                                timestamp=timezone.now(), algorithm="execute()")
        av3.save()

        av4 = Algorithm_version(algorithm_id=cls.other_user_public_algorithm,
                                timestamp=timezone.now(), algorithm="execute()")
        av4.save()

        m1 = Metrics(algorithm_version=av1, molecule=molecule, iterations=1, measurements=2,
                     circuit_depth=4, accuracy=5.2)
        m1.save()
        m2 = Metrics(algorithm_version=av2, molecule=molecule, iterations=11, measurements=12,
                     circuit_depth=14, accuracy=15.2)
        m2.save()
        m3 = Metrics(algorithm_version=av3, molecule=molecule, iterations=21, measurements=22,
                     circuit_depth=24, accuracy=25.2)
        m3.save()
        m4 = Metrics(algorithm_version=av4, molecule=molecule, iterations=31, measurements=32,
                     circuit_depth=34, accuracy=35.2)
        m4.save()

    def setUp(self):
        self.client.login(username="testuser", password="secret")

    def test_random_parameters_are_handled_correctly(self):
        response = self.client.get("/compare/a/exec()")
        self.assertEqual(response.status_code, 404)

    def test_cannot_compare_nonexistent_algorithms(self):
        response = self.client.get("/compare/10/11")
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

    def test_cannot_compare_algorithm_to_itself(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.my_algorithm.pk}"
        )
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

    def test_can_compare_to_private_by_current_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.my_private_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 200)

    def test_cannot_compare_to_private_algorithm_by_other_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.other_user_private_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 403)

    def test_can_compare_to_public_algorithm_by_other_user(self):
        response = self.client.get(
            f"/compare/{self.my_algorithm.pk}/{self.other_user_public_algorithm.pk}"
        )
        self.assertEqual(response.status_code, 200)


class WebFunctionTestViewData(TestCase):

    @classmethod
    def setUpTestAlgorithms(self):
        self.a1 = Algorithm(name='Algo1', public=True, algorithm_type=self.at1, user=self.u1,
                            article_link='https://alink1.com', github_link='https://gtlink1.com')
        self.a1.save()
        self.a2 = Algorithm(name='Algo2', public=False, algorithm_type=self.at2, user=self.u1,
                            article_link='https://alink2.com', github_link='https://gtlink2.com')
        self.a2.save()
        self.a3 = Algorithm(name='Algo3', public=True, algorithm_type=self.at1, user=self.u1,
                            article_link='https://alink3.com', github_link='https://gtlink3.com')
        self.a3.save()
        self.a4 = Algorithm(name='Algo4', public=True, algorithm_type=self.at2, user=self.u2,
                            article_link='https://alink4.com', github_link='https://gtlink4.com')
        self.a4.save()
        self.a5 = Algorithm(name='Algo5', public=False, algorithm_type=self.at3, user=self.u2,
                            article_link='https://alink5.com', github_link='https://gtlink5.com')
        self.a5.save()
        self.a6 = Algorithm(name='Algo6', public=False, algorithm_type=self.at2, user=self.u2,
                            article_link='https://alink6.com', github_link='https://gtlink6.com')
        self.a6.save()

    def setUpTestAlgorithmVersions(self):
        self.av = Algorithm_version(algorithm_id=self.a1,
                                    timestamp=datetime.datetime(2021, 2, 10, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm1\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a1,
                                    timestamp=datetime.datetime(2021, 2, 10, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm1\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a2,
                                    timestamp=datetime.datetime(2021, 2, 11, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm2\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a2,
                                    timestamp=datetime.datetime(2021, 2, 11, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm2\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a3,
                                    timestamp=datetime.datetime(2021, 2, 12, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm3\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a3,
                                    timestamp=datetime.datetime(2021, 2, 15, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm3\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a4,
                                    timestamp=datetime.datetime(2021, 2, 17, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm4\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a4,
                                    timestamp=datetime.datetime(2021, 2, 18, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm4\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a5,
                                    timestamp=datetime.datetime(2021, 2, 17, 18, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm5\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a5,
                                    timestamp=datetime.datetime(2021, 2, 18, 12, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm5\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a6,
                                    timestamp=datetime.datetime(2021, 2, 17, 9, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm6\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a6,
                                    timestamp=datetime.datetime(2021, 2, 18, 15, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm6\nversion2\n')
        self.av.save()

    @classmethod
    def setUpTestData(self):
        self.u1 = User.objects.create_user('Bob', 'bob@example.com', 'bobpassword')
        self.u1.save()
        self.u2 = User.objects.create_user('Alice', 'alice@example.com', 'alicepassword')
        self.u2.save()
        self.m1 = Molecule(name='molecule1', structure='structure1')
        self.m1.save()
        self.m2 = Molecule(name='molecule2', structure='structure2')
        self.m2.save()
        self.m3 = Molecule(name='molecule3', structure='structure3')
        self.m3.save()
        self.at1 = Algorithm_type(type_name='type1')
        self.at1.save()
        self.at2 = Algorithm_type(type_name='type2')
        self.at2.save()
        self.at3 = Algorithm_type(type_name='type3')
        self.at3.save()
        self.setUpTestAlgorithms()
        self.setUpTestAlgorithmVersions(self)

    def setUp(self):
        self.client.login(username="Bob", password="bobpassword")

    def test_my_algorithms_view_name(self):
        response = str(self.client.get("/myAlgorithms/").content)
        self.assertFalse(response.find('Algo1') < 0)
        self.assertFalse(response.find('Algo2') < 0)
        self.assertFalse(response.find('Algo3') < 0)
        self.assertTrue(response.find('Algo4') < 0)
        self.assertTrue(response.find('Algo5') < 0)
        self.assertTrue(response.find('Algo6') < 0)

    def test_my_algorithms_view_other_information(self):
        response = str(self.client.get("/myAlgorithms/").content)
        self.assertFalse(response.find('https://alink1.com') < 0)
        self.assertFalse(response.find('https://gtlink1.com') < 0)

    def test_index_view(self):
        response = str(self.client.get("/").content)
        self.assertFalse(response.find('Algo1') < 0)
        self.assertTrue(response.find('Algo2') < 0)
        self.assertFalse(response.find('Algo4') < 0)
        self.assertTrue(response.find('Algo5') < 0)

    def test_add_metrics_view(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = str(self.client.get('/addMetrics/?index=' + str(v.pk)).content)
        self.assertFalse(response.find('Algo3') < 0)

    def test_add_other_user_metrics_view(self):
        a = Algorithm.objects.get(name='Algo4')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.get('/addMetrics/?index=' + str(v.pk))
        self.assertEqual(response.status_code, 403)

    def test_add_new_version_to_other_user_algorithm(self):
        a = Algorithm.objects.get(name='Algo4')
        response = self.client.post('/addVersion/?index='+str(a.pk),
                                    {'algorithm': 'print(1)\nexec()'})
        self.assertEqual(response.status_code, 403)

    def test_add_new_version_view(self):
        a = Algorithm.objects.get(name='Algo3')
        response = str(self.client.get('/addVersion/?index='+str(a.pk)).content)
        self.assertFalse(response.find('Algo3') < 0)
        self.assertFalse(response.find('version2') < 0)

    def test_algorithm_details_view(self):
        a = Algorithm.objects.get(name='Algo3')
        response = str(self.client.get('/algorithm/'+str(a.pk)).content)
        self.assertFalse(response.find('Algo3') < 0)
        self.assertFalse(response.find('https://alink3.com') < 0)
        self.assertFalse(response.find('https://gtlink3.com') < 0)

    def test_algorithm_details_other_user_private_view(self):
        a = Algorithm.objects.get(name='Algo5')
        response = self.client.get('/algorithm/'+str(a.pk))
        self.assertEqual(response.status_code, 403)

    def test_algorithm_details_other_user_public_view(self):
        a = Algorithm.objects.get(name='Algo4')
        response = str(self.client.get('/algorithm/'+str(a.pk)).content)
        self.assertFalse(response.find('Algo4') < 0)
        self.assertFalse(response.find('https://alink4.com') < 0)
        self.assertFalse(response.find('https://gtlink4.com') < 0)

    def test_update_details(self):
        a = Algorithm.objects.get(name='Algo1')
        self.client.post('/updateAlgorithm/?index='+str(a.pk),
                         {'name': 'Algo1',
                          'algorithm_type': Algorithm_type.objects.get(type_name='type1').pk,
                          'public': 'on',
                          'article_link': 'https://aalink1.com',
                          'github_link': 'https://gtlink1.com',
                          'user': User.objects.get(username='Bob').pk})
        a = Algorithm.objects.get(name='Algo1')
        self.assertEqual(a.article_link, 'https://aalink1.com')

    def test_update_other_user_details(self):
        a = Algorithm.objects.get(name='Algo4')
        response = self.client.post('/updateAlgorithm/?index='+str(a.pk),
                                    {'name': 'Algo4',
                                     'algorithm_type': a.algorithm_type.pk,
                                     'public': 'on',
                                     'article_link': 'https://aalink4.com',
                                     'github_link': 'https://gtlink4.com',
                                     'user': User.objects.get(username='Bob').pk})
        self.assertEqual(response.status_code, 403)


class WebFunctionTestMetrics(TestCase):

    @classmethod
    def setUpTestAlgorithms(self):
        self.a1 = Algorithm(name='Algo1', public=True, algorithm_type=self.at1, user=self.u1,
                            article_link='https://alink1.com', github_link='https://gtlink1.com')
        self.a1.save()
        self.a2 = Algorithm(name='Algo2', public=False, algorithm_type=self.at2, user=self.u1,
                            article_link='https://alink2.com', github_link='https://gtlink2.com')
        self.a2.save()
        self.a3 = Algorithm(name='Algo3', public=True, algorithm_type=self.at1, user=self.u1,
                            article_link='https://alink3.com', github_link='https://gtlink3.com')
        self.a3.save()
        self.a4 = Algorithm(name='Algo4', public=True, algorithm_type=self.at2, user=self.u2,
                            article_link='https://alink4.com', github_link='https://gtlink4.com')
        self.a4.save()
        self.a5 = Algorithm(name='Algo5', public=False, algorithm_type=self.at3, user=self.u2,
                            article_link='https://alink5.com', github_link='https://gtlink5.com')
        self.a5.save()
        self.a6 = Algorithm(name='Algo6', public=False, algorithm_type=self.at2, user=self.u2,
                            article_link='https://alink6.com', github_link='https://gtlink6.com')
        self.a6.save()

    def setUpTestAlgorithmVersions(self):
        self.av = Algorithm_version(algorithm_id=self.a1,
                                    timestamp=datetime.datetime(2021, 2, 10, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm1\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a1,
                                    timestamp=datetime.datetime(2021, 2, 10, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm1\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a2,
                                    timestamp=datetime.datetime(2021, 2, 11, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm2\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a2,
                                    timestamp=datetime.datetime(2021, 2, 11, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm2\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a3,
                                    timestamp=datetime.datetime(2021, 2, 12, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm3\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a3,
                                    timestamp=datetime.datetime(2021, 2, 15, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm3\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a4,
                                    timestamp=datetime.datetime(2021, 2, 17, 10, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm4\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a4,
                                    timestamp=datetime.datetime(2021, 2, 18, 11, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm4\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a5,
                                    timestamp=datetime.datetime(2021, 2, 17, 18, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm5\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a5,
                                    timestamp=datetime.datetime(2021, 2, 18, 12, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm5\nversion2\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a6,
                                    timestamp=datetime.datetime(2021, 2, 17, 9, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm6\nversion1\n')
        self.av.save()
        self.av = Algorithm_version(algorithm_id=self.a6,
                                    timestamp=datetime.datetime(2021, 2, 18, 15, 0, 0, 0, pytz.UTC),
                                    algorithm='algorithm6\nversion2\n')
        self.av.save()

    @classmethod
    def setUpTestData(self):
        self.u1 = User.objects.create_user('Bob', 'bob@example.com', 'bobpassword')
        self.u1.save()
        self.u2 = User.objects.create_user('Alice', 'alice@example.com', 'alicepassword')
        self.u2.save()
        self.m1 = Molecule(name='molecule1', structure='structure1')
        self.m1.save()
        self.m2 = Molecule(name='molecule2', structure='structure2')
        self.m2.save()
        self.m3 = Molecule(name='molecule3', structure='structure3')
        self.m3.save()
        self.at1 = Algorithm_type(type_name='type1')
        self.at1.save()
        self.at2 = Algorithm_type(type_name='type2')
        self.at2.save()
        self.at3 = Algorithm_type(type_name='type3')
        self.at3.save()
        self.setUpTestAlgorithms()

        self.setUpTestAlgorithmVersions(self)

    def setUp(self):
        self.client.login(username="Bob", password="bobpassword")

    def test_add_metrics(self):
        a = Algorithm.objects.get(name='Algo1')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        m = Molecule.objects.get(name='molecule1')
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        metrics = Metrics.objects.get(algorithm_version=v, molecule=m)
        self.assertEqual(metrics.iterations, 1)
        self.assertEqual(metrics.measurements, 2)
        self.assertEqual(metrics.circuit_depth, 4)
        self.assertEqual(metrics.accuracy, 5.2)

    def test_add_private_metrics(self):
        a = Algorithm.objects.get(name='Algo2')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        m = Molecule.objects.get(name='molecule1')
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        metrics = Metrics.objects.get(algorithm_version=v, molecule=m)
        self.assertEqual(metrics.iterations, 1)
        self.assertEqual(metrics.measurements, 2)
        self.assertEqual(metrics.circuit_depth, 4)
        self.assertEqual(metrics.accuracy, 5.2)

    def test_add_other_users_public_metrics(self):
        a = Algorithm.objects.get(name='Algo4')
        m = Molecule.objects.get(name='molecule1')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        metrics = Metrics.objects.filter(algorithm_version=v, molecule=m)
        self.assertEqual(len(metrics), 0)

    def test_add_other_users_private_metrics(self):
        a = Algorithm.objects.get(name='Algo5')
        m = Molecule.objects.get(name='molecule1')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        metrics = Metrics.objects.filter(algorithm_version=v, molecule=m)
        self.assertEqual(len(metrics), 0)

    def test_add_one_metric(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule1')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '1',
                          'measurements': '',
                          'circuit_depth': '',
                          'accuracy': ''})
        metrics = Metrics.objects.get(algorithm_version=v, molecule=m)
        self.assertEqual(metrics.iterations, 1)
        self.assertEqual(metrics.measurements, None)
        self.assertEqual(metrics.circuit_depth, None)
        self.assertEqual(metrics.accuracy, None)

    def test_add_no_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule2')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'molecule': m.pk,
                          'algorithm_version': v.pk,
                          'iterations': '',
                          'measurements': '',
                          'circuit_depth': '',
                          'accuracy': ''})
        metrics = Metrics.objects.get(algorithm_version=v, molecule=m)
        self.assertEqual(metrics.iterations, None)
        self.assertEqual(metrics.measurements, None)
        self.assertEqual(metrics.circuit_depth, None)
        self.assertEqual(metrics.accuracy, None)

    def test_add_negative_iteration_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'molecule': m.pk,
                                     'algorithm_version': v.pk,
                                     'iterations': '-1',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Input value must be positive') < 0)

    def test_add_nonnumeric_iteration_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'molecule': m.pk,
                                     'algorithm_version': v.pk,
                                     'iterations': 'aa',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Metrics input needs to be numeric') < 0)

    def test_add_negative_accuracy_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'molecule': m.pk,
                                     'algorithm_version': v.pk,
                                     'iterations': '7',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '-3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Input value must be positive') < 0)

    def test_add_nonnumeric_accuracy_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        m = Molecule.objects.get(name='molecule3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'molecule': m.pk,
                                     'algorithm_version': v.pk,
                                     'iterations': '7',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': 'aa'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Metrics input needs to be numeric') < 0)
