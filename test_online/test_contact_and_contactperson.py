from fiken_py.models import Contact, ContactPerson
from test_online import shared_tests, sample_object_factory


def test_contact(unique_id):
    contact = sample_object_factory.contact(unique_id)

    contact.save()

    assert contact.contactId is not None

    shared_tests.attachable_object_tests(contact)

    contact_id = contact.contactId

    contact_person = sample_object_factory.contact_person(unique_id)

    actual_contact_person = contact.create_contact_person(contact_person)
    assert actual_contact_person.contactPersonId is not None
    assert actual_contact_person.name == contact_person.name

    assert actual_contact_person.contactPersonId in [cp.contactPersonId for cp in contact.contactPerson]

    actual_contact_person.delete()

    contact.delete()

    assert Contact.get(contactId=contact_id) is None