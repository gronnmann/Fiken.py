# Fiken.py
A Python implementation of the [Fiken API](https://api.fiken.no/api/v2/docs/#/contacts/createContact)

## Installation
Clone the repo
```bash
pip install fiken_py
```
You can now import the package and use it in your code.

### Private apps
To use the Fiken API you need to create a private app in Fiken. 
This will give you a private token. You can create a private app in Fiken by going to Account -> Rediger konto -> 
API -> Ny API-nøkkel

Then, either set the token globally for the whole application using:

```python
FikenObject.set_auth_token('{your_token_here}')
```

Or create it for a specific object:
```python
fiken_py = FikenPy('{your_token_here}')
```
You can then access the objects using the `fiken_py` object.

### Public apps
To use the Fiken API publically, you need to authenticate using OAuth2.
You can create a public app by going to Account -> Rediger konto -> API
-> Ny app

Then, first create an endpoint to redirect to (for example via FastAPI), and
then redirect the user to a URL retrieved from:
```python
url, state = Authorization.generate_auth_url(FIKEN_APP_ID, REDIRECT_URI)
```
This will open a window for the user to authenticate with Fiken.
When the user is authenticated, they will be redirected to the `REDIRECT_URI` with a `code` and `state` parameter.

Make sure the `state` parameter is the same as the one you generated.

Then, use the `code` to get the access token:
```python
access_token = Authorization.get_access_token_authcode(FIKEN_APP_ID, FIKEN_APP_SECRET, REDIRECT_URI, code)
```

The `redirect_uri` should be the same as the one you used to generate the URL.

Then, set the access token:

Globally:
```python
FikenObject.set_auth_token(access_token)
```

For a single object:
```python
fiken_py = FikenPy(access_token)
```


You can skip setting the client_id and client_secret if you don't wish the app to automatically 
refresh the token. That happens when doing a request, and either 1) expiry time says its expired or 2) you get a 403 error.

### Setting company slug
If you wish, you can also set the company slug globally, as its required for most API calls.
```python
FikenObject.set_company_slug('{your_company_slug_here}')
```
This is not required, and can be done on a per-call basis (using the kwargs argument).
It can also be overridden the same way.

When using an OOP-style-approach, you can get a compajny object using
```python
company = fiken_py.get_company(company_slug='your_company_slug')
```
And then use its methods to get objects related to that company.

### General syntax
All objects reside in the 'fiken_py.models' module.
They mostly correspond to the objects in the Fiken API.

Generally, all objects have the following methods:
- `get` - Fetches a single object (class method)
- `getAll` - Fetches all objects (class method)
- `save` - Saves the object to Fiken. Might need some kwargs to work properly.
- `delete` - Deletes the object from Fiken

Not all methods are available for all objects, please check the Fiken API documentation for more information.
Errors will give a `RequestWrongMediaTypeException`.

You can either access the objects directly, or use the `FikenPy` (or other object classes) to access them.


### Placeholders and kwargs
Some API calls require placeholders. These are strings that are replaced by the actual value in the API call.
For example, the URL `/companies/{companySlug}/contacts` requires the companySlug to be replaced by the actual company slug.

This is done by passing the placeholders as kwargs to the method.

Arguments passed to kwargs, but not used as placeholders, are passed as query parameters to the API call.

When doing `save` or `delete`, some of those (for example `contactId`) are fetched from
the object itself, and should not be passed as kwargs (unless you wish to override them).

### Examples - Using methods directly
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

### Examples - Using OOP-style
First, create an object and get the company:
```python
fiken_py = FikenPy('{your_token_here}')
company = fiken_py.get_company(company_slug='your_company_slug')
```

Then:

#### Getting all contacts
```python
contacts = company.get_contacts()
```

#### Getting a single contact
```python
contact = company.get_contact(contact_id='contact_id')
```

#### Creating and saving new contact
```python
contact = Contact(name="John Doe")
contact = company.create_contact(contact)
```

# Notes
Some objects do behave weirdly or not as expected.
This is a list of known quirks you might encounter:

### CreditNotePartialRequestLine and CreditNoteLine
When accessing credit notes, the lines are of type `InvoiceLine` as in the API.
However, in the API, when sending a partial credit note request, the lines are of type `creditNoteLineResult`, which
I found confusing. That type is therefore called `CreditNotePartialRequestLine` in the library.

### Draft types
The main draft type used by both Invoice, CreditNote, Offer and Order Confirmation is in the api called
`invoiceIshDraftResult`. Here they all have their own draft type, eg `InvoiceDraft` etc, all
inheriting from `InvoiceIshDraft`.

The draft types for sales and purcases in the API are `draftResult`.
Here they are split into `SalesDraft` and `PurchaseDraft`, inheriting
from `DraftOrder`.

All the methods of creating the objects from drafts, eg `createInvoice` are accessed through
the common method `draft.to_object()`.

### /accounts and /accountBalances
They both have their own class `BalanceAccount` and `BalanceAccountBalance` respectively.
The balance itself can also be fetched calling upon `balance_account_instance.get_balance()`

### Drafts and customerId/contactPersonId
Some of the POST and PUT endpoints for drafts require setting a contactId and/or contactPersonId,
while there may be multiple of those in a GET for the same field.

When saving a draft, the `contactId` and `contactPersonId` are fetched from the `customerId` and `contactPersonId` can 
either be supplised in the `kwargs`, or will be taken from the first contact in the `customerId` list
(and their first contact person).

### Saving new `Invoice` requires provoding `bankAccountCode`

When saving a new `Invoice`, you need to provide the `bankAccountCode` in the `kwargs` argument.
This is because the Invoice class itself just gives `bankAccountNumber` in the API, and we can't infer
the `bankAccountCode` from that.

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
These should only be used with a test company, as they will create and delete objects in Fiken.

To use the `test_online`, you need to set the following environment variables (in `test_online/.env`):
```dotenv
FIKEN_PRIVATE_TOKEN={your_private_token}
FIKEN_COMPANY_SLUG={your_test_company_slug}
```