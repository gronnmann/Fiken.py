# Fiken.py
A Python implementation of the [Fiken API](https://api.fiken.no/api/v2/docs/#/contacts/createContact)

## Installation
Clone the repo
```bash
pip install fiken_py
```
You can now import the package and use it in your code.

## Usage
### Private apps
To use the Fiken API you need to create a private app in Fiken. 
This will give you a private token. You can create a private app in Fiken by going to Account -> Rediger konto -> 
API -> Ny API-nøkkel

Then, set the token using the following code:
```python
FikenObject.set_auth_token('{your_token_here}')
```

If you wish, you can also set the company slug, as its required for most API calls.
```python
FikenObject.set_company_slug('{your_company_slug_here}')
```
This is not required, and can be done on a per-call basis (using the kwargs argument).
It can also be overridden the same way.

### General syntax
All objects reside in the 'fiken_py.models' module.
Mostly correspond to the objects in the Fiken API.

Generally, all objects have the following methods:
- `get` - Fetches a single object (class method)
- `getAll` - Fetches all objects (class method)
- `save` - Saves the object to Fiken
- `delete` - Deletes the object from Fiken

Not all methods are available for all objects, please check the Fiken API documentation for more information.
Errors will give a `RequestWrongMediaTypeException`.


### Placeholders and kwargs
Some API calls require placeholders. These are strings that are replaced by the actual value in the API call.
For example, the URL `/companies/{companySlug}/contacts` requires the companySlug to be replaced by the actual company slug.

This is done by passing the placeholders as kwargs to the method.

Arguments passed to kwargs, but not used as placeholders, are passed as query parameters to the API call.

When doing `save` or `delete`, some of those (for example `contactId`) are fetched from
the object itself, and should not be passed as kwargs (unless you wish to override them).

### Objects using Request classes
Some objects use different classes for create operations (POST).
For example `POST bankAccounts` uses `BankAccountRequest` instead of `BankAccount`.  
  
In those cases, create a new object of the `Request` (for example `BankAccountRequest`) class and pass it to the `save` method.
The `save` method will then respond with the actual `BankAccount` object.

### Examples
#### Getting all contacts
```python
contacts = Contact.getAll(companySlug='your_company_slug')
```

#### Getting a single contact
```python
contact = Contact.get(contactId='contact_id', companySlug='your_company_slug')
```

#### Creating and saving new contact
```python
contact = Contact(name='John Doe')
contact.save(companySlug='your_company_slug')
```

#### Deleting a contact
```python
contact = Contact.get(contactId='contact_id', companySlug='your_company_slug')
contact.delete(companySlug='your_company_slug')
```

Creating objects using Request classes:
```python
new_account_request = BankAccountCreateRequest(name='test_account', bankAccountNumber="11122233334 "
                                           , type=BankAccountType.NORMAL)
# new_account_request is <class 'fiken_py.models.bank_account.BankAccountCreateRequest'>
new_account = new_account_request.save(companySlug='fiken-demo-drage-og-elefant-as')
# new_account is <class 'fiken_py.models.bank_account.BankAccount'>
```

## Notes
Some objects do behave weirdly or not as expected.
This is a list of known quirks you might encounter:
### JournalEntryRequest maps to Transaction
The `JournalEntryRequest` object maps, when saved, returns the 
`Transaction` object in Fiken (and not `JournalEntry`).

### CreditNotePartialRequestLine and CreditNoteLine
When accessing credit notes, the lines are of type `InvoiceLine` as in the API.
However, in the API, when sending a partial credit note request, the lines are of type `creditNoteLineResult`, which
I found confusing. That type is therefore called `CreditNotePartialRequestLine` in the library.

```python
journal_entry: JournalEntryRequest

journal_entry = request.save(companySlug='fiken-demo-drage-og-elefant-as')
# returns header Location: https://api.fiken.no/api/v2/companies/fiken-demo-drage-og-elefant-as/transactions/{some id}

print(type(journal_entry)) # <class 'fiken_py.models.transaction.Transaction'>
```

## Rate limiting
From the [Fiken API documentation](https://api.fiken.no/api/v2/docs/):
> API calls may be slowed if you execute more than 4 requests per second.

The library by default tries to respect this by sleeping as to not exceed the rate limit.
This behavior can be overriden by setting:

```python
FikenObject.set_rate_limit(False)
```


## Tests
Tests are done using pytest. There's two directories with tests:
- `tests` - Tests that run locally and do not require a Fiken account
- `tests_online` - Tests that interact with the Fiken API. These require a Fiken account and a private token.
These should only be used with a test account, as they will create and delete objects in Fiken.

To use the `test_online`, you need to set the following environment variables (in `test_online/.env`):
```dotenv
FIKEN_PRIVATE_TOKEN={your_private_token}
FIKEN_COMPANY_SLUG={your_test_company_slug}
```