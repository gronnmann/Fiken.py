import os
import time

import dotenv

from fiken_py.fiken_object import FikenObject
from fiken_py.models import UserInfo, Company, BankAccount, BankAccountCreateRequest, Contact, ContactPerson
from fiken_py.fiken_types import BankAccountType

dotenv.load_dotenv(".env")

FikenObject.set_auth_token(os.getenv("FIKEN_API_TOKEN"))


def get_user_info():
    user = UserInfo.get()
    print(user)


def get_companies():
    companies = Company.getAll(sortBy='name desc')

    for company in companies:
        print(company)


def get_company():
    company = Company.get(companySlug='fiken-demo-drage-og-elefant-as')
    print(company)


def get_bank_accounts():
    # bank_accounts = BankAccount.getAll(companySlug='fiken-demo-drage-og-elefant-as')

    demo_konto = BankAccount.get(companySlug='fiken-demo-drage-og-elefant-as', bankAccountId=2882125076)
    print(demo_konto)


def create_bank_account():
    new_account = BankAccountCreateRequest(name="Testkonto", bankAccountNumber="11152233334 "
                                           , type=BankAccountType.NORMAL)
    print("Type of object in start: ", type(new_account))
    new_acc = new_account.save(companySlug='fiken-demo-drage-og-elefant-as')
    print("Type of object in end: ", type(new_acc))

    print(new_acc)
    print("New account created")


def get_contacts():
    contacts = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as')
    for c in contacts:
        print(c.name)
        # print(c)
    contact_single = Contact.get(companySlug='fiken-demo-drage-og-elefant-as', contactId=contacts[0].contactId)
    print(contact_single)


def create_and_edit_contact():
    new_contact = Contact(name="En testbruker")
    new_contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(new_contact)
    time.sleep(5)
    print(f"Before edit: {new_contact}")

    new_contact.email = "test@test.no"
    new_contact.save(companySlug='fiken-demo-drage-og-elefant-as')
    print(f"After edit: {new_contact}")


def del_test_contacts():
    contacts = Contact.getAll(companySlug='fiken-demo-drage-og-elefant-as', name="Testbruker 1")
    for c in contacts:
        print(c)
        c.delete(companySlug='fiken-demo-drage-og-elefant-as')


def create_and_edit_contact_person():
    contact_for_person = Contact(name="Bedrift med kontaktperson")
    contact_for_person.save(companySlug='fiken-demo-drage-og-elefant-as')

    contact_person = ContactPerson(name="Testperson", email="old_epost@epost.no")
    contact_person.save(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)
    print(contact_person)

    contact_person.email = "en_epost@epost.no"
    contact_person.save(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)

    print(contact_person)

    # contact_person.delete(companySlug='fiken-demo-drage-og-elefant-as', contactId=contact_for_person.contactId)
    # contact_for_person.delete(companySlug='fiken-demo-drage-og-elefant-as')


if __name__ == "__main__":
    # get_bank_accounts()
    # create_and_edit_contact()
    # create_bank_account()
    create_and_edit_contact_person()
