import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from web.models import (
    CustomUser,
    Customers,
    ItemSlot,
    SiteConfiguration,
    TimeSlot,
    Tournament,
    TournamentRegistration,
    UserSlot,
)


class ClosedClubModeTests(TestCase):
    def setUp(self):
        self.configuration = SiteConfiguration.objects.get(pk=1)
        self.customer = Customers.objects.create(
            name='Тестовый клуб',
            phone_number='+7 999 000-00-00',
            working_hours_start=datetime.time(10, 0),
            working_hours_end=datetime.time(12, 0),
        )
        self.table = ItemSlot.objects.create(
            name='Стол 1',
            customer=self.customer,
        )
        self.time_slot = TimeSlot.objects.filter(customer=self.customer).first()
        self.user = CustomUser.objects.create_user(
            username='player',
            password='test-password',
        )
        self.tournament = Tournament.objects.create(
            customer=self.customer,
            name='Тестовый турнир',
            date=datetime.date.today() + datetime.timedelta(days=1),
            start_time=datetime.time(10, 0),
            end_time=datetime.time(11, 0),
            max_participants=8,
            min_participants=1,
            registration_deadline=timezone.now(),
            description='Описание',
        )
        self.tournament.tables.add(self.table)
        self.client.force_login(self.user)

    def set_closed_mode(self, is_closed):
        self.configuration.is_closed = is_closed
        self.configuration.closed_title = 'Клуб завершил работу'
        self.configuration.closed_message = 'Запись и бронирование остановлены.'
        self.configuration.gratitude_message = 'Спасибо организаторам и всем участникам!'
        self.configuration.save()

    def test_closed_mode_replaces_public_content(self):
        self.set_closed_mode(True)

        response = self.client.get(reverse('daily_schedule'))

        self.assertContains(response, 'Клуб завершил работу')
        self.assertContains(response, 'Запись и бронирование остановлены.')
        self.assertContains(response, 'Спасибо организаторам и всем участникам!')
        self.assertNotContains(response, '>Бронь<')
        self.assertNotContains(response, '>Расписание за день<')
        self.assertNotContains(response, 'Privacy Policy')

    def test_closed_mode_blocks_booking_and_registration(self):
        self.set_closed_mode(True)

        booking_response = self.client.get(reverse('book_slot', args=[
            self.time_slot.id,
            self.table.id,
            datetime.date.today().isoformat(),
        ]))
        registration_response = self.client.get(
            reverse('register_tournament', args=[self.tournament.id])
        )

        self.assertRedirects(booking_response, reverse('index'), fetch_redirect_response=False)
        self.assertRedirects(registration_response, reverse('index'), fetch_redirect_response=False)
        self.assertFalse(UserSlot.objects.exists())
        self.assertFalse(TournamentRegistration.objects.exists())

    def test_disabling_closed_mode_restores_actions(self):
        self.set_closed_mode(False)

        self.client.get(
            reverse('book_slot', args=[
                self.time_slot.id,
                self.table.id,
                datetime.date.today().isoformat(),
            ]),
            HTTP_REFERER=reverse('daily_schedule'),
        )
        self.client.get(reverse('register_tournament', args=[self.tournament.id]))

        self.assertTrue(UserSlot.objects.filter(user=self.user).exists())
        self.assertTrue(TournamentRegistration.objects.filter(
            user=self.user,
            tournament=self.tournament,
        ).exists())
