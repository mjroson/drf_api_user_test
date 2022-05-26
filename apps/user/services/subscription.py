from django.conf import settings

import requests

from ..models import SubscriptionChoices


class SubscriptionService:
    """
        Class to handler connection with subscription service.
    """
    @classmethod
    def is_user_suscribed(self, user_id) -> dict:
        """
            Check if user has a active subscription
        """
        return requests.get(f"https://subscriptions.fake.service.test/api/v1/users/{user_id}").json()["subscription"]


class SubscriptionServiceMock:

    @classmethod
    def is_user_suscribed(self, user_id) -> dict:
        return SubscriptionChoices.ACTIVE.value


if settings.SUBSCRIPTION_SERVICE_MOCK:
    SubscriptionService = SubscriptionServiceMock # noqa
