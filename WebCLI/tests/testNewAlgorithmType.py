from ddf import M, N
from django.contrib.auth.models import User
from django.test import Client, TestCase

from ..models import Algorithm_type


class TestNewAlgorithmType(TestCase):

    def setUp(self):
        client = Client()
        self.test_user = N(User, username=M(r'________'), password=M(r'________'))
        client.post(
            '/signup/',
            {'username': self.test_user.username,
             'password1': self.test_user.password, 'password2': self.test_user.password}
        )
        self.client.post(
             '/accounts/login/',
             {'username': self.test_user.username, 'password': self.test_user.password})

    def test_add_type(self):
        test_algotype = N(Algorithm_type, type_name=M(r'--- (-----)'))
        self.client.post('/newAlgorithmType/',
                         {'type_name': test_algotype.type_name})
        result = Algorithm_type.objects.get(type_name=test_algotype.type_name)
        self.assertIsNotNone(result)
