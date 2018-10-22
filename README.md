# json-legaliser

Python util designed for assessing json object structure. 


##Examples
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

You can find much more usage examples in `test.py` file.