from django.test import TestCase, Client
from ddf import M, N
from django.contrib.auth.models import User


class testLogin(TestCase):
    def test_signup(self):
        client = Client()
        test_user = N(User, username=M(r'________'), password=M(r'________'))
        response = client.post(
            '/signup/',
            {'username': test_user.username,
             'password1': test_user.password, 'password2': test_user.password}
        )
        self.assertEqual(response.status_code, 302)
        response = client.login(username=test_user.username, password=test_user.password)
        self.assertEqual(response, True)

    def test_login(self):
        client = Client()
        test_user = N(User, username=M(r'________'), password=M(r'________'))
        response = client.post(
            '/signup/',
            {'username': test_user.username,
             'password1': test_user.password, 'password2': test_user.password}
        )
        client.post(
            '/accounts/login/',
            {'username': test_user.username, 'password': test_user.password})
        response = str(client.get('/').content)
        self.assertFalse(response.find(f'logged in - {test_user.username}') < 0)

    def test_logout(self):
        client = Client()
        test_user = N(User, username=M(r'________'), password=M(r'________'))
        response = client.post(
            '/signup/',
            {'username': test_user.username,
             'password1': test_user.password, 'password2': test_user.password}
        )
        client.post(
            '/accounts/login/',
            {'username': test_user.username, 'password': test_user.password})
        client.get('/accounts/logout/')
        response = str(client.get('/').content)
        self.assertTrue(response.find(f'logged in - {test_user.username}') < 0)
