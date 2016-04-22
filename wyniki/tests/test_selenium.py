from django import test
from selenium import webdriver

from wyniki import models
from wyniki.tests import factories


class SeleniumTest(test.LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.candidates = [
            factories.KandydatFactory(nazwa="Kandydat A"),
            factories.KandydatFactory(nazwa="Kandydat B")
        ]
        self.commune = factories.GminaFactory()
        self.results = [
            models.Wynik.objects.create(gmina=self.commune, kandydat=self.candidates[0], liczba=1000),
            models.Wynik.objects.create(gmina=self.commune, kandydat=self.candidates[1], liczba=2000)
        ]

    def test_get(self):
        self.browser.get(self.live_server_url)

        xpath = "/html/body/div[5]/div/div[2]/table/tbody/tr[2]/td[3]"
        element = self.browser.find_element_by_xpath(xpath)
        self.assertEquals(element.text, "1000")
