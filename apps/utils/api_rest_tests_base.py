from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.user.factories import UserFactory


class BaseApiTests(APITestCase):
    __test__ = False
    object_factory = None
    url_base_name = None
    BATCH_SIZE = 3

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Create a initial user.
        cls.user = cls.make_user_auth()

    @classmethod
    def make_user_auth(self):
        return UserFactory(is_staff=True)

    def setUp(self, *args, **kwargs):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def get_url_base_name(self):
        if not self.url_base_name:
            raise NotImplementedError("url_base_name attribute is not defined")
        return self.url_base_name

    def get_list_query_params(self):
        """
        Change queryparams for all list
        """
        return {}

    def get_url_list(self):
        return reverse(f"{self.get_url_base_name()}-list")

    def get_url_detail(self, id):
        return reverse(f"{self.url_base_name}-detail", args=[id])

    def create(self, data):
        return self.client.post(self.get_url_list(), data, format='json')

    def detail(self, id):
        return self.client.get(self.get_url_detail(id), format='json')

    def update(self, id, data):
        return self.client.put(self.get_url_detail(id), data, format='json')

    def partial_update(self, id, data):
        return self.client.patch(self.get_url_detapartial_updateil(id), data, format='json')

    def delete(self, id):
        return self.client.delete(self.get_url_detail(id), format='json')

    def get_list(self, params: dict = {}):
        """
        Use params to test on a specific list or get_list_query_params() for all list
        """
        return self.client.get(
            self.get_url_list(),
            {**self.get_list_query_params(), **params},
            format="json",
        )

    def get_extra_kwargs_for_create(self):
        """
        Used to define parameters for creation
        """
        return {}

    def test_model_list_should_return_200(self, *args, **kwargs):
        data = {
            "size": self.BATCH_SIZE,
        }

        self.object_factory.create_batch(**data, **self.get_extra_kwargs_for_create())
        response = self.get_list()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertEqual(len(response.data), self.BATCH_SIZE)

    def test_model_detail_should_return_200(self, *args, **kwargs):
        data = {}

        obj = self.object_factory.create(**data, **self.get_extra_kwargs_for_create())
        url = self.get_url_detail(obj.id)

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(obj.id))
