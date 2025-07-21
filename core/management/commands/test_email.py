# core/management/commands/test_email.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='The email address to send the test email to')

    def handle(self, *args, **options):
        email = options['email']
        try:
            send_mail(
                'KilimoPesa Email Test',
                'This is a test email from KilimoPesa',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))