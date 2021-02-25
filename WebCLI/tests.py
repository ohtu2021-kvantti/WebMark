from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Molecule, Algorithm_type, Algorithm, Algorithm_version
from django.urls import reverse
from django.utils import timezone
import datetime
import pytz


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
        a = Algorithm.objects.get(name='test_algorithm')
        self.c.post('/addVersion/?index='+str(a.pk),
                    {'algorithm': 'print(1)\nexec()'})
        v = Algorithm_version.objects.filter(algorithm_id=a)

        self.assertEqual(a.public, True)
        self.assertEqual(a.algorithm_type.type_name, 'VQE')
        self.assertEqual(a.user.username, 'testuser3')
        self.assertEqual(a.molecule.name, 'Hydrogen')
        self.assertEqual(len(v), 2)
        self.assertEqual(v[1].algorithm, 'print(1)\nexec()')


class WebFunctionTestMyAlgorithmsView(TestCase):
    @classmethod
    def setUpTestData(cls):
        User.objects.create_user("testuser", "test@example.com", "secret")

    def setUp(self):
        self.client.login(username="testuser", password="secret")

    def test_my_algorithms_view(self):
        response = self.client.get("/myAlgorithms/")
        self.assertEqual(response.status_code, 200)


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
            algorithm_type=algorithm_type, molecule=molecule, public=True
        )
        cls.my_private_algorithm = Algorithm.objects.create(
            user=user, name="my private algorithm",
            algorithm_type=algorithm_type, molecule=molecule, public=False
        )
        cls.other_user_public_algorithm = Algorithm.objects.create(
            user=other_user, name="other user public algorithm",
            algorithm_type=algorithm_type, molecule=molecule, public=True
        )
        cls.other_user_private_algorithm = Algorithm.objects.create(
            user=other_user, name="other user private algorithm",
            algorithm_type=algorithm_type, molecule=molecule, public=False
        )

        cls.my_algorithm.save()
        cls.my_private_algorithm.save()
        cls.other_user_private_algorithm.save()
        cls.other_user_public_algorithm.save()

        Algorithm_version(algorithm_id=cls.my_algorithm, timestamp=timezone.now(),
                          algorithm="execute()").save()
        Algorithm_version(algorithm_id=cls.my_private_algorithm, timestamp=timezone.now(),
                          algorithm="execute()").save()
        Algorithm_version(algorithm_id=cls.other_user_private_algorithm, timestamp=timezone.now(),
                          algorithm="execute()").save()
        Algorithm_version(algorithm_id=cls.other_user_public_algorithm, timestamp=timezone.now(),
                          algorithm="execute()").save()

    def setUp(self):
        self.client.login(username="testuser", password="secret")

    def test_random_parameters_are_handled_correctly(self):
        response = self.client.get("/compare/a/exec()")
        self.assertRedirects(response, reverse("home"), status_code=302, target_status_code=200)

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
    def setUpTestData(cls):
        u1 = User.objects.create_user('Bob', 'bob@example.com', 'bobpassword')
        u1.save()
        u2 = User.objects.create_user('Alice', 'alice@example.com', 'alicepassword')
        u2.save()
        m1 = Molecule(name='molecule1', structure='structure1')
        m1.save()
        m2 = Molecule(name='molecule2', structure='structure2')
        m2.save()
        m3 = Molecule(name='molecule3', structure='structure3')
        m3.save()
        at1 = Algorithm_type(type_name='type1')
        at1.save()
        at2 = Algorithm_type(type_name='type2')
        at2.save()
        at3 = Algorithm_type(type_name='type3')
        at3.save()
        a1 = Algorithm(name='Algo1', public=True, molecule=m1, algorithm_type=at1, user=u1,
                       article_link='https://alink1.com', github_link='https://gtlink1.com')
        a1.save()
        a2 = Algorithm(name='Algo2', public=False, molecule=m1, algorithm_type=at2, user=u1,
                       article_link='https://alink2.com', github_link='https://gtlink2.com')
        a2.save()
        a3 = Algorithm(name='Algo3', public=True, molecule=m2, algorithm_type=at1, user=u1,
                       article_link='https://alink3.com', github_link='https://gtlink3.com')
        a3.save()
        a4 = Algorithm(name='Algo4', public=True, molecule=m3, algorithm_type=at2, user=u2,
                       article_link='https://alink4.com', github_link='https://gtlink4.com')
        a4.save()
        a5 = Algorithm(name='Algo5', public=False, molecule=m2, algorithm_type=at3, user=u2,
                       article_link='https://alink5.com', github_link='https://gtlink5.com')
        a5.save()
        a6 = Algorithm(name='Algo6', public=False, molecule=m1, algorithm_type=at2, user=u2,
                       article_link='https://alink6.com', github_link='https://gtlink6.com')
        a6.save()
        av = Algorithm_version(algorithm_id=a1,
                               timestamp=datetime.datetime(2021, 2, 10, 10, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm1\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a1,
                               timestamp=datetime.datetime(2021, 2, 10, 11, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm1\nversion2\n')
        av.save()
        av = Algorithm_version(algorithm_id=a2,
                               timestamp=datetime.datetime(2021, 2, 11, 10, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm2\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a2,
                               timestamp=datetime.datetime(2021, 2, 11, 11, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm2\nversion2\n')
        av.save()
        av = Algorithm_version(algorithm_id=a3,
                               timestamp=datetime.datetime(2021, 2, 12, 10, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm3\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a3,
                               timestamp=datetime.datetime(2021, 2, 15, 11, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm3\nversion2\n')
        av.save()
        av = Algorithm_version(algorithm_id=a4,
                               timestamp=datetime.datetime(2021, 2, 17, 10, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm4\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a4,
                               timestamp=datetime.datetime(2021, 2, 18, 11, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm4\nversion2\n')
        av.save()
        av = Algorithm_version(algorithm_id=a5,
                               timestamp=datetime.datetime(2021, 2, 17, 18, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm5\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a5,
                               timestamp=datetime.datetime(2021, 2, 18, 12, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm5\nversion2\n')
        av.save()
        av = Algorithm_version(algorithm_id=a6,
                               timestamp=datetime.datetime(2021, 2, 17, 9, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm6\nversion1\n')
        av.save()
        av = Algorithm_version(algorithm_id=a6,
                               timestamp=datetime.datetime(2021, 2, 18, 15, 0, 0, 0, pytz.UTC),
                               algorithm='algorithm6\nversion2\n')
        av.save()

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
        self.assertFalse(response.find('molecule1') < 0)
        self.assertFalse(response.find('https://alink1.com') < 0)
        self.assertFalse(response.find('https://gtlink1.com') < 0)

    def test_index_view(self):
        response = str(self.client.get("/").content)
        self.assertFalse(response.find('Algo1') < 0)
        self.assertTrue(response.find('Algo2') < 0)
        self.assertFalse(response.find('Algo4') < 0)
        self.assertTrue(response.find('Algo5') < 0)

    def test_add_metrics(self):
        a = Algorithm.objects.get(name='Algo1')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, 1)
        self.assertEqual(v2.measurements, 2)
        self.assertEqual(v2.circuit_depth, 4)
        self.assertEqual(v2.accuracy, 5.2)

    def test_add_private_metrics(self):
        a = Algorithm.objects.get(name='Algo2')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, 1)
        self.assertEqual(v2.measurements, 2)
        self.assertEqual(v2.circuit_depth, 4)
        self.assertEqual(v2.accuracy, 5.2)

    def test_add_other_users_public_metrics(self):
        a = Algorithm.objects.get(name='Algo4')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, None)

    def test_add_other_users_private_metrics(self):
        a = Algorithm.objects.get(name='Algo5')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '1',
                          'measurements': '2',
                          'circuit_depth': '4',
                          'accuracy': '5.2'})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, None)

    def test_add_one_metric(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '1',
                          'measurements': '',
                          'circuit_depth': '',
                          'accuracy': ''})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, 1)
        self.assertEqual(v2.measurements, None)
        self.assertEqual(v2.circuit_depth, None)
        self.assertEqual(v2.accuracy, None)

    def test_add_no_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        self.client.post('/addMetrics/?index=' + str(v.pk),
                         {'iterations': '',
                          'measurements': '',
                          'circuit_depth': '',
                          'accuracy': ''})
        v2 = Algorithm_version.objects.get(pk=v.pk)
        self.assertEqual(v2.iterations, None)
        self.assertEqual(v2.measurements, None)
        self.assertEqual(v2.circuit_depth, None)
        self.assertEqual(v2.accuracy, None)

    def test_add_negative_iteration_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'iterations': '-1',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Input value must be positive') < 0)

    def test_add_nonumeric_iteration_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'iterations': 'aa',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Metrics input needs to be numeric') < 0)

    def test_add_negative_accuracy_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'iterations': '7',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': '-3.1'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Input value must be positive') < 0)

    def test_add_nonumeric_accuracy_metrics(self):
        a = Algorithm.objects.get(name='Algo3')
        v = Algorithm_version.objects.filter(algorithm_id=a)[0]
        response = self.client.post('/addMetrics/?index=' + str(v.pk),
                                    {'iterations': '7',
                                     'measurements': '1',
                                     'circuit_depth': '2',
                                     'accuracy': 'aa'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(str(response.content).find('Metrics input needs to be numeric') < 0)

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
