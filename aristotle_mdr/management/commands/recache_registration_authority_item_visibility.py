from django.core.management.base import BaseCommand, CommandError
from aristotle_mdr.models import RegistrationAuthority

class Command(BaseCommand):
    args = '<workgroup_id workgroup_id ...>'
    help = 'Recomputes and caches the public andlocked statuses for the given workgroup(s). This is useful if the registration authorities associated with a workgroup change.'

    def handle(self, *args, **options):
        for ra_id in args:
            try:
                ra = RegistrationAuthority.objects.get(pk=int(ra_id))
            except RegistrationAuthority.DoesNotExist:
                raise CommandError('Registration Authority "%s" does not exist' % ra_id)
            self.stdout.write('Beginning update for items in Registration Authority "%s" (id:%s)' % (ra.name,ra_id,))

            for item in ra.items.all():
                item.recache_states()
            self.stdout.write('Successfully updated items in Registration Authority "%s" (id:%s)' % (ra.name,ra_id,))
