from rest_framework import status

from apps.utils.api_rest_tests_base import BaseApiTests

from ..factories import GroupFactory, UserFactory
from ..models import SubscriptionChoices
from ..serializers import MinimalUserModelSerializer


class BaseUserApiTest(BaseApiTests):

    object_factory = UserFactory
    url_base_name = 'api:users'

    @classmethod
    def make_super_user(self):
        return UserFactory(is_superuser=True)

    @classmethod
    def make_staff_user(self):
        return UserFactory(is_staff=True, is_superuser=False)

    @classmethod
    def make_regular_user(self):
        return UserFactory(is_staff=False, is_superuser=False)

    def get_base_user_data(self):
        return {
            "first_name": "John",
            "last_name": "Doe",
            "email": "johndoe@ine.test",
            "password": "SuperSecurePasswd",
            "repeat_password": "SuperSecurePasswd",
            "groups": []
        }


class UserApiAsStaffTests(BaseUserApiTest):
    __test__ = True

    def test_create_user(self, *args, **kwargs):
        """
            Test happy path.
            Check if some attribute of user was creating as succesfully
        """
        data = {
            **self.get_base_user_data(),
            "username": "johndo",
        }

        response = self.create(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get('subscription'), SubscriptionChoices.ACTIVE.value)
        self.assertIsNotNone(response.data.get('created'))
        self.assertIsNotNone(response.data.get('updated'))
        self.assertIsNotNone(response.data.get('id'))

    def test_create_user_not_match_password(self, *args, **kwargs):
        data = {
            **self.get_base_user_data(),
            "username": "johndo2",
            "repeat_password": "notmatch",
        }
        response = self.create(data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_user_with_group_already_exist(self, *args, **kwargs):
        groups_name = ["sales", "support"]

        for name in groups_name:
            GroupFactory(name=name)

        data = {
            **self.get_base_user_data(),
            "username": "johndo3",
            "groups": groups_name
        }

        response = self.create(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_with_group_dont_exist(self, *args, **kwargs):
        data = {
            **self.get_base_user_data(),
            "username": "johndo3",
            "groups": [
                "not_exists"
            ]
        }

        response = self.create(data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_user(self, *args, **kwargs):
        """
            Check if group changes
        """
        user = UserFactory()

        user_data = MinimalUserModelSerializer(instance=user).data
        groups = [GroupFactory(name="group10")]

        data = {
            **user_data,
            "groups": [group.name for group in groups],
            "password": "qwerty123$",
            "repeat_password": "qwerty123$"
        }
        response = self.update(user.id, data)

        self.assertEqual(len(response.data.get("groups", [])), len(groups))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_regular_user(self, *args, **kwargs):
        user = self.make_regular_user()

        response = self.delete(user.id)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_staff_user(self, *args, **kwargs):
        user = self.make_staff_user()

        response = self.delete(user.id)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UserApiAsAdminTests(BaseUserApiTest):
    __test__ = True

    @classmethod
    def make_user_auth(cls):
        return cls.make_super_user()

    def test_delete_staff_user(self, *args, **kwargs):
        user = self.make_staff_user()

        response = self.delete(user.id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class UserApiAsRegularTests(BaseUserApiTest):
    __test__ = True

    @classmethod
    def make_user_auth(cls):
        return cls.make_regular_user()

    def test_create_user(self, *args, **kwargs):
        data = {
            **self.get_base_user_data(),
            "username": "johndo1",
        }

        response = self.create(data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_user(self, *args, **kwargs):
        """
            Check if group not changes
        """
        old_password = "qwerty123$"
        user = UserFactory(password=old_password, username="unique10")

        user_data = MinimalUserModelSerializer(instance=user).data
        groups = [GroupFactory(name="group11")]

        new_password = "asdfgh123$"
        data = {
            **user_data,
            "groups": [group.name for group in groups],
            "old_password": old_password,
            "password": new_password,
            "repeat_password": new_password
        }
        response = self.update(user.id, data)

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.groups.all().count(), 0)
        self.assertTrue(user.check_password(new_password))

    def test_update_user_without_old_password(self, *args, **kwargs):
        user = UserFactory()
        user_data = MinimalUserModelSerializer(instance=user).data
        new_password = "new_password1234%2$F"
        data = {
            **user_data,
            "password": new_password,
            "repeat_password": new_password
        }
        response = self.update(user.id, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_user(self, *args, **kwargs):
        user = self.make_regular_user()
        response = self.delete(user.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_detail_user(self, *args, **kwargs):
        user = UserFactory()
        response = self.detail(user.id)

        forbidden_fields = [
            "groups",
            "created",
            "subscription",
            "updated",
        ]

        for field in forbidden_fields:
            self.assertIsNone(response.data.get(field))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
