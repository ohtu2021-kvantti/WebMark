from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Molecule, Algorithm_type, Algorithm
from ..models import Algorithm_version, Metrics
from django.urls import reverse
from django.utils import timezone


class TestUpdateAlgorithm(TestCase):
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

        av1 = Algorithm_version(algorithm_id=cls.my_algorithm,
                                timestamp=timezone.now(),
                                algorithm='algo description',
                                circuit="circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))",
                                optimizer_module='scipy',
                                optimizer_method='BFGS')
        av1.save()

        av2 = Algorithm_version(algorithm_id=cls.my_private_algorithm,
                                timestamp=timezone.now(),
                                algorithm='algo description',
                                circuit="circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))",
                                optimizer_module='scipy',
                                optimizer_method='BFGS')
        av2.save()

        av3 = Algorithm_version(algorithm_id=cls.other_user_private_algorithm,
                                timestamp=timezone.now(),
                                algorithm='algo description',
                                circuit="circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))",
                                optimizer_module='scipy',
                                optimizer_method='BFGS')
        av3.save()

        av4 = Algorithm_version(algorithm_id=cls.other_user_public_algorithm,
                                timestamp=timezone.now(),
                                algorithm='algo description',
                                circuit="circuit:\nRy(target=(0,), parameter=a)\nX(target=(2,))",
                                optimizer_module='scipy',
                                optimizer_method='BFGS')
        av4.save()

        m1 = Metrics(algorithm_version=av1, molecule=molecule, gate_depth=1, qubit_count=2,
                     average_iterations=4, success_rate=5.2)
        m1.save()
        m2 = Metrics(algorithm_version=av2, molecule=molecule, gate_depth=11, qubit_count=12,
                     average_iterations=14, success_rate=15.2)
        m2.save()
        m3 = Metrics(algorithm_version=av3, molecule=molecule, gate_depth=21, qubit_count=22,
                     average_iterations=24, success_rate=25.2)
        m3.save()
        m4 = Metrics(algorithm_version=av4, molecule=molecule, gate_depth=31, qubit_count=32,
                     average_iterations=34, success_rate=35.2)
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
