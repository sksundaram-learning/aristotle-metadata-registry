from django.core.management.base import BaseCommand, CommandError
from aristotle_mdr.models import Workgroup

class Command(BaseCommand):
    args = '<workgroup_id workgroup_id ...>'
    help = 'Recomputes and caches the public andlocked statuses for the given workgroup(s). This is useful if the registration authorities associated with a workgroup change.'

    def handle(self, *args, **options):
        for wg_id in args:
            try:
                wg = Workgroup.objects.get(pk=int(wg_id))
            except Workgroup.DoesNotExist:
                raise CommandError('Workgroup "%s" does not exist' % wg_id)
            self.stdout.write('Beginning update for items in Workgroup "%s" (id:%s)' % (wg.name,wg_id,))

            for item in wg.items.all():
                item.recache_states()
            self.stdout.write('Successfully updated items in Workgroup "%s" (id:%s)' % (wg.name,wg_id,))
