from fiken_py.models import Contact
from test_online import shared_tests


def test_contact(unique_id):
    contact = Contact(name=f"Test contact ({unique_id})")

    contact.save()

    assert contact.contactId is not None

    shared_tests.attachable_object_tests(contact)

    contact_id = contact.contactId

    contact.delete()

    assert Contact.get(contactId=contact_id) is None