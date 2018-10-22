import types


class LegaliserException(Exception):
    def __str__(self):
        return '%s' % self.message


class LegaliserTypeException(LegaliserException):
    def __init__(self, expected, got_type, got, pointer):
        self.pointer = pointer
        self.expected = expected
        self.got, self.got_type = got, got_type
        self.message = 'At .{} expecting type {}, got "{}" of {} type instead'.format(
            '.'.join(pointer), expected.__name__, got, got_type.__name__)


class LegaliserValueException(LegaliserException):
    def __init__(self, expected, got, pointer):
        self.pointer = pointer
        self.expected = expected
        self.got = got
        self.message = 'At .{} expecting value of "{}", got "{}" instead'.format(
            '.'.join(pointer), expected, got)


class LegaliserKeysNotPresentException(LegaliserException):
    def __init__(self, expected, pointer):
        self.pointer = pointer
        self.expected = expected
        self.message = 'At .{} expecting key{} "{}", but not found'.format(
            '.'.join(pointer), 's' if len(expected) > 1 else '', ', '.join(map(str, expected)))


class LegaliserTooManyKeysPresentException(LegaliserException):
    def __init__(self, got, pointer):
        self.pointer = pointer
        self.got = got
        self.message = 'At .{} not expected key{} "{}" found'.format(
            '.'.join(pointer), 's' if len(got) > 1 else '', ', '.join(map(str, got)))


class LegaliserCriteriaException(LegaliserException):
    def __init__(self, criteria, pointer):
        self.pointer = pointer
        self.criteria = criteria
        self.message = 'At .{} function {} failed'.format(
            '.'.join(pointer), criteria.__name__)


class LegaliserCriteriaOtherException(LegaliserException):
    def __init__(self, criteria, pointer, exception):
        self.pointer = pointer
        self.criteria = criteria
        self.exception = exception
        self.message = 'At .{} function {} failed raising: {}'.format(
            '.'.join(pointer), criteria.__name__, repr(exception))


class Many(object):
    def __init__(self, of_type):
        self.of_type = of_type

    def __getitem__(self, item):
        return self.of_type


class Option(object):
    pass


class Optional(Option):
    pass


class AnyType(Option):
    pass


def __assert_criteria(fn, arg, pointer):
    try:
        ret = fn(arg)
    except Exception as e:
        raise LegaliserCriteriaOtherException(criteria=fn, pointer=pointer, exception=e)
    else:
        if not ret:
            raise LegaliserCriteriaException(criteria=fn, pointer=pointer)


def __assert_type(source_value, source_type, schema_type, schema, pointer):
    if schema_type == tuple:
        pass
    elif schema_type == Many:
        if isinstance(schema.of_type, type):
            assert schema.of_type == source_type, pointer
        else:
            assert isinstance(source_type, schema.of_type), pointer
    elif schema_type == type:
        if schema == AnyType:
            pass
        elif schema != source_type:
            raise LegaliserTypeException(expected=schema, got=source_value,
                                         got_type=source_type, pointer=pointer)
    else:
        assert source_type == schema_type, pointer


def __assert_value(source_value, schema_type, schema, pointer):
    if schema_type == dict:
        schema_keys = set(schema.keys())
        schema_must_keys = set((k for k in schema if schema[k] != Optional and not
                               (isinstance(schema[k], tuple) and Optional in schema[k][1:])))
        source_keys = set(source_value.keys())
        too_few_keys = schema_must_keys - source_keys
        if too_few_keys:
            raise LegaliserKeysNotPresentException(expected=too_few_keys, pointer=pointer)
        too_many_keys = source_keys - schema_keys
        if too_many_keys:
            raise LegaliserTooManyKeysPresentException(got=too_many_keys, pointer=pointer)
        for (k, v) in source_value.items():
            legalise_element(v, schema[k], pointer + [str(k)])
    elif schema_type == list:
        many_elements_schema = None
        for i, element in enumerate(source_value):
            if many_elements_schema is None:
                if isinstance(schema[i], Many):
                    many_elements_schema = schema[i].of_type
            legalise_element(element, many_elements_schema or schema[i], pointer)
    elif schema_type == tuple:
        legalise_element(source_value, schema[0], pointer)
        for sch in schema[1:]:
            if isinstance(sch, (types.FunctionType, types.MethodType)):
                __assert_criteria(fn=schema[1], arg=source_value, pointer=pointer)
    elif schema_type == Many:
        legalise_element(source_value, schema.of_type, pointer)
    elif schema_type == type:
        if schema == AnyType:
            pass
        else:
            assert isinstance(source_value, schema), pointer
    else:
        if source_value != schema:
            raise LegaliserValueException(expected=schema, got=source_value, pointer=pointer)


def legalise_element(e, schema=None, pointer=None):
    pointer = pointer or []
    if schema is None:
        schema = dict
    source_type, schema_type = type(e), type(schema)
    __assert_type(source_value=e, source_type=source_type,
                  schema_type=schema_type, schema=schema, pointer=pointer)
    __assert_value(source_value=e, schema_type=schema_type,
                   schema=schema, pointer=pointer)


def legalise(json_object, schema=None):
    return legalise_element(e=json_object, schema=schema)
