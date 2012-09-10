"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

__test__ = {"doctest": """
Another way to test that 1 + 1 is equal to 2.

>>> 1 + 1 == 2
True
"""}

class ViewTest(TestCase):
	fixtures = ['test_data.json']
	
	def setUp(self):
		self.client = Client()
	
	def test_register_page(self):
		data = {
			'username': 'testuserme',
			'email': 'testme@testworld.com',
			'password1': 'pass12345',
			'password2': 'pass12345'
		}
		response = self.client.post('/register/', data)
		self.assertRedirects(response, '/register/success/')
	
	def test_bookmark_save(self):
		response = self.client.login(
			username = 'marco',
			password = 'marco'
		)
		self.assertTrue(response, msg='Failed to login')
		
		data = {
			'url': 'http://www.example.com/',
			'title': 'Test URL',
			'tags': 'test-tag1 test-tag2'
		}
		response = self.client.post('/save/', data)
		self.assertRedirects(response, '/user/marco/')
		
		response = self.client.get('/user/marco/')
		self.assertContains(response, 'http://www.example.com/')
		self.assertContains(response, 'Test URL')
		self.assertContains(response, 'test-tag1')
		self.assertContains(response, 'test-tag2')

