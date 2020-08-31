from django.test import TestCase, Client
from django.urls import reverse

from LinkShortener import models
from LinkShortener.models import Link


class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        link_db = models.Link()
        link_db.original = 'https://www.google.com/'
        link_db.hash = link_db.get_hash()
        link_db.save()
        link_db = models.Link()
        link_db.original = 'https://www.google.com/'
        link_db.hash = link_db.get_hash()
        link_db.save()

    def test_call_view_home_get(self):
        """ Testing the "home" view with GET method"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertNotContains(response, 'Shortened link:')

    def test_call_view_home_post_empty_link(self):
        """ Testing the "home" view with POST method with empty link"""
        url = reverse('home')
        response = self.client.post(url, {'url': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Empty field')

    def test_call_view_home_post_wrong_link(self):
        """ Testing the "home" view with POST method with invalid link"""
        url = reverse('home')
        response = self.client.post(url, {'url': 'https://sdfsdfsdf   www.google.com/'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Incorrect URL:')

    def test_call_view_home_post_normal_link(self):
        """ Testing the "home" view with POST method with valid link"""
        url = reverse('home')
        response = self.client.post(url, {'url': 'https://www.google.com/'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, 'Shortened link:')

    def test_call_view_links_get(self):
        """ Testing the "links" view with GET method"""
        url = reverse('links')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'links.html')
        links = response.context['links']
        self.assertCountEqual(links, Link.objects.all())

    def test_call_view_redirect_error(self):
        """ Testing the "redir" view with invalid hash"""
        url = reverse('redir', args=['sdsfa'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_call_view_redirect_true(self):
        """ Testing the "redir" view with valid hash"""
        url = reverse('redir', args=[Link.objects.all()[1].hash])
        response = self.client.get(url)
        self.assertEquals(response.status_code, 302)
        self.assertEquals(Link.objects.all()[1].redir_num, 1)

    def test_call_view_delete(self):
        """ Testing the "delete" view """
        url = reverse('delete', kwargs={'linkid': 1})
        response = self.client.get(url, {'id': 1})
        self.assertRedirects(response, '/links/', status_code=302, target_status_code=200, fetch_redirect_response=True)
        self.assertEquals(Link.objects.all().count(), 1)
