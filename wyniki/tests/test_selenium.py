import unittest

import time
from django.contrib.auth.models import User
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from wyniki import models
from wyniki.tests import factories


class FixtureMixin:
    def set_up_database(self):
        self.candidates = [
            factories.KandydatFactory(nazwa="Kandydat A"),
            factories.KandydatFactory(nazwa="Kandydat B")
        ]
        self.commune = factories.GminaFactory()
        self.results = [
            models.Wynik.objects.create(gmina=self.commune, kandydat=self.candidates[0], liczba=1000),
            models.Wynik.objects.create(gmina=self.commune, kandydat=self.candidates[1], liczba=2000)
        ]


class SeleniumTest(FixtureMixin, StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.set_up_database()

    def test_get(self):
        self.browser.get(self.live_server_url)

        time.sleep(0.1)

        xpath = "/html/body/div[5]/div/div[2]/table/tbody/tr[2]/td[3]"
        element = self.browser.find_element_by_xpath(xpath)
        self.assertEquals(element.text, "1000")

    def test_commune_list_unavailable_not_logged(self):
        self.browser.get(self.live_server_url)

        time.sleep(0.1)

        xpath = "(//tbody[@data-table='commune_type']//span[@data-row-link])[1]"
        element = self.browser.find_element_by_xpath(xpath)
        element.click()

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_class_name("edit-results")

    def test_commune_list(self):
        User.objects.create_user("blah", None, "blah")

        self.browser.get(self.live_server_url)

        time.sleep(0.1)

        self.browser.find_element_by_xpath("//input[@name='username']").send_keys("blah")
        self.browser.find_element_by_xpath("//input[@name='password']").send_keys("blah")
        self.browser.find_element_by_xpath("//input[@name='submit']").click()

        time.sleep(0.1)

        self.assertIn("Dzień dobry", self.browser.find_element_by_tag_name("body").text)

        xpath = "(//tbody[@data-table='commune_type']//span[@data-row-link])[1]"
        element = self.browser.find_element_by_xpath(xpath)
        element.click()

        time.sleep(0.1)

        self.browser.find_element_by_xpath("//span[@class='edit-results']")


class SeleniumBrokenConnectionTest(FixtureMixin, StaticLiveServerTestCase):

    def setUp(self):
        self.browser = webdriver.Chrome()
        self.set_up_database()

    def test_broken_connection(self):
        self.browser.get(self.live_server_url)

        time.sleep(0.1)

        self.server_thread.terminate()
        self.server_thread.join()

        time.sleep(0.1)

        xpath = "(//tbody[@data-table='commune_type']//span[@data-row-link])[1]"
        element = self.browser.find_element_by_xpath(xpath)
        element.click()

        self.assertIn("połączenia", self.browser.find_element_by_tag_name("body").text)
