from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import factory
from faker import Factory

User = get_user_model()

faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        django_get_or_create = ('username',)

    first_name = factory.LazyAttribute(lambda _: faker.name())
    last_name = factory.LazyAttribute(lambda _: faker.name())
    email = factory.LazyAttribute(lambda _: faker.email())
    username = factory.LazyAttribute(lambda _: faker.slug())


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
