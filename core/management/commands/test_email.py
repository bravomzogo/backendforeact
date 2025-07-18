from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email sending configuration'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test to')

    def handle(self, *args, **options):
        recipient = options['email']
        
        try:
            send_mail(
                'KilimoPesa Email Test',
                'This is a test email from KilimoPesa.',
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent test email to {recipient}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Failed to send email: {str(e)}'))