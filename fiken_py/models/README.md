# Creating model instances

To create model instances, you need to inherit from 
`BaseModel` (pydantic) and `FikenObject` (fiken_py).
You can then add your own properties as needed from pydantic.

```python
from fiken_py.models import BaseModel, FikenObject

class MyModel(BaseModel, FikenObject):
    model_required_property: str
    model_optional_property: Optional[str] = None
    pass
```

Depending on which methods you wish to support, you then need to set up class variables
for URL paths. The following paths are available:
```python
_GET_PATH_SINGLE = 'gets single object'
_GET_PATH_MULTIPLE = 'gets a list of objects'
_POST_PATH = 'creates a new object'
_PUT_PATH = 'updates an object'
_DELETE_PATH = 'deletes an object'
```

You also need to specify the id-attribute by overriding the property `id_attr`
and specifying the name and value of the attribute.

Example (from `models/bank_account.py`):
```python
@property
def id_attr(self):
    return "bankAccountId", self.bankAccountId
```

### Request classes
If you are using a method that requires a different request and response class, you need to make the response class
extend the `FikenObjectRequiringRequest`, and then overriding the `_to_request_object` method.
The application will then automatically convert into the request class when using `POST` or `PUT` methods.

```python
from fiken_py.models import BaseModel, FikenObjectRequiringRequest

class MyModel(BaseModel, FikenObjectRequiringRequest):
    _POST_PATH = '{post path here}'
    
    model_required_property: str
    model_optional_property: Optional[str] = None
    pass

    def _to_request_object(self, **kwargs) -> 'MyModelRequest':
        return MyModelRequest(
            model_required_property=self.model_required_property
        )
        
        # or - using the built-in method which will automatically embed all common properties
        return BankAccountRequest(
            **FikenObjectRequiringRequest._pack_common_fields(self, MyModelRequest)
        )
    
class MyModelRequest(BaseModel):
    model_required_property: str
    
    pass
```

### Adding tests
When adding a new model, you should also add tests for the model.

For general GET testing, create a snake case file under `test/sample_model_responses/{snake_case_model_name}.json`
with expected responses from the API.  
Then, add the Model class to the `test/test_models.py` file in the `test_object_methods` list.

```python
@pytest.mark.parametrize("object", [
    ...
    MyModel,
])
def test_object_methods(object: FikenObject, m: requests_mock.Mocker):
    ...
```