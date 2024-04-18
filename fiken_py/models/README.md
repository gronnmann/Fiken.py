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

If you wish to support `PUT`, you also need a `@property` method called `is_new` which decides
when to use `POST` and when to use `PUT`.
Check out `contact.py` for an example.

```python
@property
def is_new(self) -> bool:
    return self.id is None
```

### Request classes
If you are using a method that requires a different request and response class, you can
create the Response class as normal, then create a request class that extends `FikenObjectRequest` instead of
`FikenObject`. You then need to set up `BASE_CLASS` to point to the response class.

```python
from fiken_py.models import BaseModel, FikenObject, FikenObjectRequest

class MyModel(BaseModel, FikenObject):
    model_required_property: str
    model_optional_property: Optional[str] = None
    pass

class MyModelRequest(BaseModel, FikenObjectRequest):
    _POST_PATH = '{post path here}'
    
    BASE_CLASS: ClassVar[FikenObject] = MyModel
    pass
```
The `BASE_CLASS` is used to determine the response class when calling the `post` method.

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