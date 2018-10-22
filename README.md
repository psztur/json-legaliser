# json-legaliser

Python util designed for assessing json object structure. 


## Examples
In order to ensure your json object consist only of key `person` with a value of string
and key `phone` with numeric value: 
```python
from legaliser import legalise

data = {'person': 'John', 'phone': 123454321}
legalise(json_object=data, schema={'person': str, 'phone': int})
```

There are different types of exceptions method `legalise` raise if an object being passed
does not meet desired structure.
```python
from legaliser import legalise

data = {'person': 'John', 'phone': 'abcdef'}
legalise(json_object=data, schema={'person': str, 'phone': int})
```
will raise such an exception:
```
legaliser.LegaliserTypeException: At .phone expecting type int, got "abcdef" of str type instead
```


You can catch such exception and wrap it with your application:
```
>>> import legaliser
>>> 
>>> data = {'person': 'John', 'phone': 'abcdef'}
>>> try:
...     legaliser.legalise(json_object=data, schema={'person': str, 'phone': int})
... except legaliser.LegaliserTypeException as e:
...     if e.pointer == ['phone'] and e.got_type == str:
...         print 'Please provide numeric phone number instead of a string'
... 
Please provide numeric phone number instead of a string
>>> 
```

## More complex example
```python
from legaliser import legalise, Many, Optional

data = {'status': 'WARMING UP',
        'temperatures': {'pcb1': 60, 'pcb2': 42.7},
        'queued measurements': [12353, 65463, 76346, 34542, 34544, 87547]}
legalise(json_object=data,
         schema={'status': str,
                 'temperatures': (dict, Optional),
                 'queued measurements': [Many(int)]})
```

The structure above will also accept such input data, as field `temperatures` is optional:
```python
data = {'status': 'WARMING UP',
        'queued measurements': [12353, 65463, 76346, 34542, 34544, 87547]}
```

You can write custom methods for data validation: 
```python

from legaliser import legalise

data = {'queued measurements': [12353, 65463, 76346, 34542, 34544, 87547]}
def validate_measurement(values):
    for val in values:
        if not 1000 < val < 99999:
            return False
    return True

legalise(json_object=data,
         schema={'queued measurements': (list, validate_measurement)})
```