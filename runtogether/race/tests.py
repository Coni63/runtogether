from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from runtogether.city.models import City
from runtogether.race.models import Race

User = get_user_model()


class RaceViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("testuser", "test@example.com", "password")
        self.city1 = City.objects.create(name="Paris", latitude=48.8566, longitude=2.3522)
        self.city2 = City.objects.create(name="Versailles", latitude=48.8049, longitude=2.1204)  # Approx 17km from Paris
        self.city3 = City.objects.create(name="Marseille", latitude=43.2965, longitude=5.3698)  # Far from Paris

        self.user.city = self.city1
        self.user.save()

        self.race1 = Race.objects.create(name="Race in Paris", city=self.city1, distance=[10, 21])
        self.race2 = Race.objects.create(name="Race in Versailles", city=self.city2, distance=[5, 10])
        self.race3 = Race.objects.create(name="Race in Marseille", city=self.city3, distance=[42])

    def test_list_races_authenticated_user_with_city(self):
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("race:races"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.race1.name)
        self.assertContains(response, self.race2.name)  # Versailles is within 40km
        self.assertNotContains(response, self.race3.name)

    def test_list_races_authenticated_user_with_city_outside_radius(self):
        # Change user city to be far from all races
        self.user.city = self.city3
        self.user.save()
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("race:races"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, self.race1.name)
        self.assertNotContains(response, self.race2.name)
        self.assertContains(response, self.race3.name)

    def test_list_races_authenticated_user_without_city(self):
        self.user.city = None
        self.user.save()
        self.client.login(username="testuser", password="password")
        response = self.client.get(reverse("race:races"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.race1.name)
        self.assertContains(response, self.race2.name)
        self.assertContains(response, self.race3.name)

    def test_list_races_unauthenticated_user(self):
        response = self.client.get(reverse("race:races"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.race1.name)
        self.assertContains(response, self.race2.name)
        self.assertContains(response, self.race3.name)
