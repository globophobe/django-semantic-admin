from faker import Faker

from factory import LazyAttribute
from factory.django import DjangoModelFactory

from .models import Person

fake = Faker()


class PersonFactory(DjangoModelFactory):
    name = LazyAttribute(lambda x: fake.first_name())
    url = LazyAttribute(lambda x: fake.safe_domain_name())
    email = LazyAttribute(lambda x: fake.email())
    birthday = LazyAttribute(lambda x: fake.past_date())

    class Meta:
        model = Person
