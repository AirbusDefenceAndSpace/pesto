import os
from pesto.ws.features.converter.array_converter import ArrayConverter
from pesto.ws.features.converter.metadata_converter import MetadataConverter
from pesto.ws.features.converter.object_converter import ObjectConverter
from pesto.ws.features.converter.primitive_converter import PrimitiveConverter
from pesto.ws.features.converter.image_converter import ImageConverter

primitive_schemas = [{'type': _} for _ in ['number', 'string', 'float', 'int', 'bool']]
metadata_schemas = [{'$ref': _} for _ in ['#/definitions/Metadata', '#/definitions/Metadatas']]
image_schemas = [{'$ref': _} for _ in ['#/definitions/Image', '#/definitions/Images']]


def convert(x, schema):
    return 1 if x == 2 else 0


def test_image_converter():
    c = ImageConverter(None)

    value = os.path.join(os.path.dirname(__file__), "resources", "image.tif")
    value = 'file://{}'.format(value)

    for schema in image_schemas:
        assert c.match(schema)
        output = c.convert((value, schema))
        assert len(output.shape) == 3
    for schema in primitive_schemas:
        assert c.match(schema) is False


def test_metadata_converter():
    c = MetadataConverter()
    value = 'this is a random value'

    for schema in metadata_schemas:
        assert c.match(schema)
        assert c.convert((value, schema)) == value
    for schema in primitive_schemas:
        assert c.match(schema) is False


def test_primitive_converter():
    c = PrimitiveConverter()
    value = 'this is a random value'
    for schema in primitive_schemas:
        assert c.match(schema)
        assert c.convert((value, schema)) == value


def test_array_converter():
    c = ArrayConverter(convert)
    value = {'items': [2, 2, 1, 2, 3]}
    schema = {
        'type': 'array',
        'items': 'number'
    }

    assert c.match(schema)
    output = c.convert((value, schema))
    assert output == [convert(_, None) for _ in value]


def test_object_converter():
    c = ObjectConverter(convert)
    value = {
        'a': 2,
        'b': 'toto'
    }
    schema = {
        'type': 'object',
        'properties': {
            'a': {
                'type': 'number'
            },
            'b': {
                'type': 'string'
            }
        }
    }
    assert c.match(schema)

    output = c.convert((value, schema))
    for k, v in output.items():
        assert v == convert(value[k], schema['properties'][k])
