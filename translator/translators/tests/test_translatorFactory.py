from django.contrib.auth.models import User
from django.test import TestCase
from translator.models import SocialNetwork, HasSocialNetwork


class TestTranslatorFactory(TestCase):
    fixtures = ["socialNetworks", "family_family", "family_userProfiles", "users", "hasSocialNetworks"]

    def test_build(self):
        from translator.translators.TranslatorFactory import TranslatorFactory
        snf = SocialNetwork(shortName="falseSN", name="Fake Social Network")
        snf.save()
        farodrig = User.objects.get(username="farodrig")
        hsn = HasSocialNetwork(user=farodrig, social=snf, username="falseUsername")
        hsn.save()
        for sn in SocialNetwork.objects.all():
            sender = HasSocialNetwork.objects.filter(social=sn, user__username="farodrig").first()
            kind = sender.social.pk
            translator = TranslatorFactory.build(sender)
            if kind == "falseSN":
                self.assertIsNone(translator)
            else:
                self.assertEqual(kind, translator.socialID)

    def test_getPushHandler(self):
        from translator.translators.TranslatorFactory import TranslatorFactory
        for sn in SocialNetwork.objects.all():
            if sn.pushNotification:
                handler = TranslatorFactory.getPushHandler(sn)
                self.assertIsNotNone(handler)
            else:
                self.assertRaises(ValueError, TranslatorFactory.getPushHandler, sn)
