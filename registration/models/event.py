from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django_bleach.models import BleachField
from multiselectfield import MultiSelectField

from badges.models import BadgeSettings, BadgeDefaults, Badge
from gifts.models import HelpersGifts
from inventory.models import InventorySettings


def _default_mail():
    return settings.FROM_MAIL


@python_2_unicode_compatible
class Event(models.Model):
    class Meta:
        ordering = ['name', 'url_name']

    """ Event for registration.

    Columns:
        :url_name: the ID of the event used in URLs
        :name: the name of the event
        :text: text at begin of registration
        :imprint: text at the bottom if the registration page
        :registered: text after the successful registration
        :email: e-mail address used as sender of automatic e-mails
        :active: is the registration opened?
        :admins: list of admins of this event, they can see and edit everything
        :ask_shirt: ask for the t-shirt size during registration
        :ask_vegetarian: ask, if the helper is vegetarian
        :show_public_numbers: show the number of current and maximal helpers on
                             the registration page
        :mail_validation: helper must validate his mail address by a link
        :badge: use the badge creation system
    """

    SHIRT_UNKNOWN = 'UNKNOWN'
    SHIRT_NO = 'NO'
    SHIRT_S = 'S'
    SHIRT_M = 'M'
    SHIRT_L = 'L'
    SHIRT_XL = 'XL'
    SHIRT_XXL = 'XXL'
    SHIRT_S_GIRLY = 'S_GIRLY'
    SHIRT_M_GIRLY = 'M_GIRLY'
    SHIRT_L_GIRLY = 'L_GIRLY'
    SHIRT_XL_GIRLY = 'XL_GIRLY'

    SHIRT_CHOICES = (
        (SHIRT_UNKNOWN, _('Unknown')),
        (SHIRT_NO, _('I do not want a T-Shirt')),
        (SHIRT_S, _('S')),
        (SHIRT_M, _('M')),
        (SHIRT_L, _('L')),
        (SHIRT_XL, _('XL')),
        (SHIRT_XXL, _('XXL')),
        (SHIRT_S_GIRLY, _('S (girly)')),
        (SHIRT_M_GIRLY, _('M (girly)')),
        (SHIRT_L_GIRLY, _('L (girly)')),
        (SHIRT_XL_GIRLY, _('XL (girly)')),
    )

    url_name = models.CharField(
        max_length=200,
        unique=True,
        validators=[RegexValidator('^[a-zA-Z0-9]+$')],
        verbose_name=_("Name for URL"),
        help_text=_("May contain the following chars: a-zA-Z0-9."),
    )

    name = models.CharField(
        max_length=200,
        verbose_name=_("Event name"),
    )

    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_("First day of event"),
    )

    text = BleachField(
        blank=True,
        verbose_name=_("Text before registration"),
        help_text=_("Displayed as first text of the registration form."),
    )

    imprint = BleachField(
        blank=True,
        verbose_name=_('Imprint'),
        help_text=_("Display at the bottom of the registration form."),
    )

    registered = BleachField(
        blank=True,
        verbose_name=_("Text after registration"),
        help_text=_("Displayed after registration."),
    )

    email = models.EmailField(
        default=_default_mail,
        verbose_name=_("E-Mail"),
        help_text=_("Used as Reply-to address for mails sent to helpers"),
    )

    # note: there is code to duplicate the file in forms/event.py
    logo = models.ImageField(
        upload_to='logos',
        blank=True,
        null=True,
        verbose_name=_("Logo"),
    )

    max_overlapping = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_("Maximal overlapping of shifts"),
        help_text=_("If two shifts overlap more than this value in minutes "
                    "it is not possible to register for both shifts. Leave "
                    "empty to disable this check."),
    )

    admins = models.ManyToManyField(
        User,
        blank=True,
    )

    active = models.BooleanField(
        default=False,
        verbose_name=_("Registration publicly visible"),
    )

    ask_shirt = models.BooleanField(
        default=True,
        verbose_name=_("Ask for T-shirt size"),
    )

    ask_vegetarian = models.BooleanField(
        default=True,
        verbose_name=_("Ask, if helper is vegetarian"),
    )

    ask_full_age = models.BooleanField(
        default=True,
        verbose_name=_("Helpers have to confirm to be full age")
    )

    ask_news = models.BooleanField(
        default=True,
        verbose_name=_("Ask if helper wants to be notified about new events"),
    )

    show_public_numbers = models.BooleanField(
        default=True,
        verbose_name=_("Show number of helpers on registration page"),
    )

    mail_validation = models.BooleanField(
        default=True,
        verbose_name=_("Registrations for public shifts must be validated by "
                       "a link that is sent per mail"),
    )

    badges = models.BooleanField(
        default=False,
        verbose_name=_("Use badge creation"),
    )

    gifts = models.BooleanField(
        default=False,
        verbose_name=_("Manage gifts for helpers"),
    )

    inventory = models.BooleanField(
        default=False,
        verbose_name=_("Use the inventory functionality"),
    )

    archived = models.BooleanField(
        default=False,
        verbose_name=_("Event is archived"),
    )

    shirt_sizes = MultiSelectField(
        choices=filter(lambda e: e[0] != 'UNKNOWN', SHIRT_CHOICES),
        default=list(filter(lambda e: e not in ('UNKNOWN', 'NO'),
                       [e[0] for e in SHIRT_CHOICES])),
        verbose_name=_("Available T-shirt sizes"),
    )

    def __str__(self):
        return self.name

    def clean(self):
        # the shirt sizes of the helpers must be selected in shirt_sizes
        # this means that it is not possible to disable a size as long one
        # helper has selected this size
        if self.ask_shirt:
            not_removable = []

            new_choices = self.get_shirt_choices()
            for choice in Event.SHIRT_CHOICES:
                if choice not in new_choices:
                    if self.helper_set.filter(shirt=choice[0]).exists():
                        not_removable.append(choice[1])

            if not_removable:
                sizes = ', '.join(map(str, not_removable))
                raise ValidationError({'shirt_sizes':
                                       _("The following sizes are used and "
                                         "therefore cannot be removed: {}".
                                         format(sizes))})

    def is_admin(self, user):
        """ Check, if a user is admin of this event and returns a boolean.

        A superuser is also admin of an event.

        :param user: the user
        :type user: :class:`django.contrib.auth.models.User`

        :returns: True or False
        """
        return user.is_superuser or self.admins.filter(pk=user.pk).exists()

    def is_involved(self, user):
        """ Check if is_admin is fulfilled or the user is admin of a job.

        :param user: the user
        :type user: :class:`django.contrib.auth.models.User`
        """
        if self.is_admin(user):
            return True

        # iterate over all jobs
        for job in self.job_set.all():
            if job.job_admins.filter(pk=user.pk).exists():
                return True

        return False

    def get_shirt_choices(self, internal=True):
        choices = []

        for shirt in Event.SHIRT_CHOICES:
            if (shirt[0] == Event.SHIRT_UNKNOWN and internal) or \
                    shirt[0] in self.shirt_sizes:
                choices.append(shirt)

        return choices

    @property
    def public_jobs(self):
        return self.job_set.filter(public=True)

    @property
    def badge_settings(self):
        try:
            return self.badgesettings
        except AttributeError:
            return None

    @property
    def inventory_settings(self):
        try:
            return self.inventorysettings
        except AttributeError:
            return None

    @property
    def all_coordinators(self):
        result = []

        # iterate over jobs
        for job in self.job_set.all():
            for c in job.coordinators.all():
                if c not in result:
                    result.append(c)

        return result


@receiver(post_save, sender=Event, dispatch_uid='event_saved')
def event_saved(sender, instance, using, **kwargs):
    """ Add badge settings, badges and gifts if necessary.

    This is a signal handler, that is called, when a event is saved. It
    adds the badge settings if badge creation is enabled and it is not
    there already. It also adds badge defaults to all jobs and badges to all
    helpers and coordinators if necessary.
    """
    if instance.badges:
        # badge settings for event
        if not instance.badge_settings:
            settings = BadgeSettings()
            settings.event = instance
            settings.save()

        # badge defaults for jobs
        for job in instance.job_set.all():
            if not job.badge_defaults:
                defaults = BadgeDefaults()
                defaults.save()

                job.badge_defaults = defaults
                job.save()

        # badge for coordinators
        # TODO: should not be necessary?
        for coordinator in instance.all_coordinators:
            if not hasattr(coordinator, 'badge'):
                badge = Badge()
                badge.helper = coordinator
                badge.save()

        # badge for helpers
        for helper in instance.helper_set.all():
            if not hasattr(helper, 'badge'):
                badge = Badge()
                badge.helper = helper
                badge.save()

    if instance.gifts:
        for helper in instance.helper_set.all():
            if not hasattr(helper, 'gifts'):
                gifts = HelpersGifts()
                gifts.helper = helper
                gifts.save()

    if instance.inventory:
        if not instance.inventory_settings:
            InventorySettings.objects.create(event=instance)
