import json

from django.core.urlresolvers import reverse
from django.test import TestCase


class TestUsername(TestCase):
    def test_anonymous(self):
        response = self.client.get(reverse("username"))
        data = json.loads(response.content.decode('utf-8'))
        self.assertFalse(data['is_authenticated'])
