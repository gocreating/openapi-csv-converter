import yaml

from utils import str2bool
from models import OasPath, OasSchema, OasProperty, OasPolymorphicProperty

spec = {}

def property_id_to_spec(property_id):
    oas_property = OasProperty.findDictById(property_id)
    oas_property_type = oas_property.get('data_type')
    property_spec = {}
    validation_extras = {}

    property_nullable = oas_property.get('nullable')
    if property_nullable != None:
        validation_extras['nullable'] = str2bool(property_nullable)

    if oas_property_type == 'string':
        property_spec['type'] = 'string'

        string_min_length = oas_property.get('string_min_length')
        string_max_length = oas_property.get('string_max_length')
        string_format = oas_property.get('string_format')
        string_pattern = oas_property.get('string_pattern')
        string_enum = oas_property.get('string_enum')

        if string_min_length != None:
            validation_extras['minLength'] = string_min_length
        if string_max_length != None:
            validation_extras['maxLength'] = string_max_length
        if string_format != None:
            validation_extras['format'] = string_format
        if string_pattern != None:
            validation_extras['pattern'] = string_pattern
        if string_enum != None:
            validation_extras['enum'] = string_enum.split(',')

        return { **property_spec, **validation_extras }

    elif oas_property_type == 'number':
        property_spec['type'] = 'number'

        number_format = oas_property.get('number_format')
        number_minimum = oas_property.get('number_minimum')
        number_exclusive_minimum = oas_property.get('number_exclusive_minimum')
        number_maximum = oas_property.get('number_maximum')
        number_exclusive_maximum = oas_property.get('number_exclusive_maximum')
        number_multiple_of = oas_property.get('number_multiple_of')

        if number_format != None:
            validation_extras['format'] = number_format
        if number_minimum != None:
            validation_extras['minimum'] = float(number_minimum)
        if number_exclusive_minimum != None:
            validation_extras['exclusiveMinimum'] = str2bool(number_exclusive_minimum)
        if number_maximum != None:
            validation_extras['maximum'] = float(number_maximum)
        if number_exclusive_maximum != None:
            validation_extras['exclusiveMaximum'] = str2bool(number_exclusive_maximum)
        if number_multiple_of != None:
            validation_extras['multipleOf'] = float(number_multiple_of)

        return { **property_spec, **validation_extras }

    elif oas_property_type == 'integer':
        property_spec['type'] = 'integer'

        integer_format = oas_property.get('integer_format')
        integer_minimum = oas_property.get('integer_minimum')
        integer_exclusive_minimum = oas_property.get('integer_exclusive_minimum')
        integer_maximum = oas_property.get('integer_maximum')
        integer_exclusive_maximum = oas_property.get('integer_exclusive_maximum')
        integer_multiple_of = oas_property.get('integer_multiple_of')

        if integer_format != None:
            validation_extras['format'] = integer_format
        if integer_minimum != None:
            validation_extras['minimum'] = int(integer_minimum)
        if integer_exclusive_minimum != None:
            validation_extras['exclusiveMinimum'] = str2bool(integer_exclusive_minimum)
        if integer_maximum != None:
            validation_extras['maximum'] = int(integer_maximum)
        if integer_exclusive_maximum != None:
            validation_extras['exclusiveMaximum'] = str2bool(integer_exclusive_maximum)
        if integer_multiple_of != None:
            validation_extras['multipleOf'] = float(integer_multiple_of)

        return { **property_spec, **validation_extras }

    elif oas_property_type == 'boolean':
        property_spec['type'] = 'boolean'
        return { **property_spec, **validation_extras }

    # valid type in json schema
    elif oas_property_type == 'null':
        property_spec['type'] = 'null'
        return { **property_spec, **validation_extras }

    elif oas_property_type == 'array':
        property_spec['type'] = 'array'
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            property_spec['items'] = property_id_to_spec(oas_polymorphic_property.get('partial_property_id'))
        return { **property_spec, **validation_extras }

    elif oas_property_type == 'object':
        property_spec['type'] = 'object'
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        if len(oas_polymorphic_properties) > 0:
            property_spec['properties'] = {}
            required_properties = []

            for oas_polymorphic_property in oas_polymorphic_properties:
                partial_property_id = oas_polymorphic_property.get('partial_property_id')
                partial_property = OasProperty.findDictById(partial_property_id)
                partial_property_name = partial_property.get('property_name')
                partial_property_required = partial_property.get('object_required')
                if partial_property_required != None and str2bool(partial_property_required):
                    required_properties.append(partial_property_name)
                property_spec['properties'][partial_property_name] = property_id_to_spec(partial_property_id)
            if len(required_properties) > 0:
                property_spec['required'] = required_properties
            additional_properties = oas_property.get('object_additional_properties')
            if additional_properties != None:
                property_spec['additionalProperties'] = str2bool(additional_properties)
        return { **property_spec, **validation_extras }

    elif oas_property_type == 'oneOf':
        property_spec['oneOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['oneOf'].append(property_id_to_spec(partial_property_id))
        return { **property_spec, **validation_extras }

    elif oas_property_type == 'anyOf':
        property_spec['anyOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['anyOf'].append(property_id_to_spec(partial_property_id))
        return { **property_spec, **validation_extras }

    elif oas_property_type == 'allOf':
        property_spec['allOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['allOf'].append(property_id_to_spec(partial_property_id))
        return { **property_spec, **validation_extras }

    elif oas_property_type == '$ref':
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        ref_schema_id = oas_polymorphic_properties[0].get('ref_schema_id')
        ref_schema = OasSchema.findDictById(ref_schema_id)
        ref_schema_name = ref_schema.get('schema_name')
        property_spec['$ref'] = f'#/components/schemas/{ref_schema_name}'
        return { **property_spec, **validation_extras }

    else:
        raise Exception('Invalid property.')

def handle_oas_component_schema():
    spec['components'] = { 'schemas': {} }
    for row in OasSchema.rows:
        schema = OasSchema.toDict(row)
        schema_name = schema.get('schema_name')
        if schema_name:
            schema_spec = property_id_to_spec(schema.get('property_id'))
            spec['components']['schemas'][schema_name] = schema_spec

def handle_oas_path_schema():
    spec['paths'] = {}
    for row in OasPath.rows:
        path = OasPath.toDict(row)
        request_body_schema = OasSchema.findDictById(path.get('request_body_schema_id'))
        property_id = request_body_schema.get('property_id')
        fuck = property_id_to_spec(property_id)
        spec['paths'][path.get('oas_path')] = {}
        spec['paths'][path.get('oas_path')][path.get('oas_operation')] = {
            'requestBody': {
                'content': {
                    'application/json': {
                        'schema': fuck
                    }
                }
            }
        }

def csv2oas():
    OasPath.load()
    OasSchema.load()
    OasProperty.load()
    OasPolymorphicProperty.load()

    handle_oas_component_schema()
    handle_oas_path_schema()

    with open('build/oas.yaml', 'w') as yaml_file:
        yaml.dump(spec, yaml_file, allow_unicode=True)

csv2oas()
