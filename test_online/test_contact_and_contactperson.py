from fiken_py.models import Contact, ContactPerson
from test_online import shared_tests


def test_contact(unique_id):
    contact = Contact(name=f"Test contact ({unique_id})")

    contact.save()

    assert contact.contactId is not None

    shared_tests.attachable_object_tests(contact)

    contact_id = contact.contactId

    contact_person = ContactPerson(
        name=f"Ola {unique_id}",
        email="test@test.com",
        phoneNumber="123456789",
    )

    actual_contact_person = contact.create_contact_person(contact_person)
    assert actual_contact_person.contactPersonId is not None
    assert actual_contact_person.name == contact_person.name

    assert actual_contact_person.contactPersonId in [cp.contactPersonId for cp in contact.contactPerson]

    actual_contact_person.delete()

    contact.delete()

    assert Contact.get(contactId=contact_id) is None