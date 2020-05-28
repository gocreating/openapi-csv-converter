import yaml

from argparse import ArgumentParser
from utils import str2bool
from models import OasPath, OasSchema, OasProperty, OasPolymorphicProperty

parser = ArgumentParser()
parser.add_argument("-s", "--spec-file", dest="spec_path")
args = parser.parse_args()

schemaNameIdMap = {}

def handle_oas_property(oas_property, oas_property_name=None, property_object_required=None):
    oas_property_type = oas_property.get('type')

    validation_extras = {}

    property_nullable = oas_property.get('nullable')
    if property_nullable != None:
        validation_extras['nullable'] = property_nullable
    if property_object_required != None:
        validation_extras['object_required'] = property_object_required

    if oas_property_type == 'string':
        string_min_length = oas_property.get('minLength')
        string_max_length = oas_property.get('maxLength')
        string_format = oas_property.get('format')
        string_pattern = oas_property.get('pattern')
        string_enums = oas_property.get('enum')

        if string_min_length != None:
            validation_extras['string_min_length'] = string_min_length
        if string_max_length != None:
            validation_extras['string_max_length'] = string_max_length
        if string_format != None:
            validation_extras['string_format'] = string_format
        if string_pattern != None:
            validation_extras['string_pattern'] = string_pattern
        if string_enums != None:
            validation_extras['string_enum'] = ','.join(string_enums)

        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='string', **validation_extras)
        return oas_property_id

    elif oas_property_type == 'number':
        number_format = oas_property.get('format')
        number_minimum = oas_property.get('minimum')
        number_exclusive_minimum = oas_property.get('exclusiveMinimum')
        number_maximum = oas_property.get('maximum')
        number_exclusive_maximum = oas_property.get('exclusiveMaximum')
        number_multiple_of = oas_property.get('multipleOf')

        if number_format != None:
            validation_extras['number_format'] = number_format
        if number_minimum != None:
            validation_extras['number_minimum'] = number_minimum
        if number_exclusive_minimum != None:
            validation_extras['number_exclusive_minimum'] = number_exclusive_minimum
        if number_maximum != None:
            validation_extras['number_maximum'] = number_maximum
        if number_exclusive_maximum != None:
            validation_extras['number_exclusive_maximum'] = number_exclusive_maximum
        if number_multiple_of != None:
            validation_extras['number_multiple_of'] = number_multiple_of

        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='number', **validation_extras)
        return oas_property_id

    elif oas_property_type == 'integer':
        integer_format = oas_property.get('format')
        integer_minimum = oas_property.get('minimum')
        integer_exclusive_minimum = oas_property.get('exclusiveMinimum')
        integer_maximum = oas_property.get('maximum')
        integer_exclusive_maximum = oas_property.get('exclusiveMaximum')
        integer_multiple_of = oas_property.get('multipleOf')

        if integer_format != None:
            validation_extras['integer_format'] = integer_format
        if integer_minimum != None:
            validation_extras['integer_minimum'] = integer_minimum
        if integer_exclusive_minimum != None:
            validation_extras['integer_exclusive_minimum'] = integer_exclusive_minimum
        if integer_maximum != None:
            validation_extras['integer_maximum'] = integer_maximum
        if integer_exclusive_maximum != None:
            validation_extras['integer_exclusive_maximum'] = integer_exclusive_maximum
        if integer_multiple_of != None:
            validation_extras['integer_multiple_of'] = integer_multiple_of

        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='integer', **validation_extras)
        return oas_property_id

    elif oas_property_type == 'boolean':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='boolean', **validation_extras)
        return oas_property_id

    # valid type in json schema
    elif oas_property_type == 'null':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='null')
        return oas_property_id

    elif oas_property_type == 'array':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='array', **validation_extras)
        prop = oas_property.get('items')
        partial_property_id = handle_oas_property(prop)
        OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property_type == 'object':
        additional_properties = oas_property.get('additionalProperties')
        oas_property_id = OasProperty.add(property_name=oas_property_name,
                                          data_type='object',
                                          object_additional_properties=additional_properties if additional_properties != None else None,
                                          **validation_extras)
        requried_properties = oas_property.get('required')
        for prop_name, prop in oas_property.get('properties', {}).items():
            partial_property_id = handle_oas_property(prop, prop_name, True if requried_properties != None and prop_name in requried_properties else None)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('oneOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='oneOf', **validation_extras)
        for prop in oas_property.get('oneOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('anyOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='anyOf', **validation_extras)
        for prop in oas_property.get('anyOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('allOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='allOf', **validation_extras)
        for prop in oas_property.get('allOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('$ref'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='$ref', **validation_extras)
        schema_name = oas_property.get('$ref').replace('#/components/schemas/', '')
        ref_schema_id = schemaNameIdMap.get(schema_name)
        OasPolymorphicProperty.add(property_id=oas_property_id, ref_schema_id=ref_schema_id)
        return oas_property_id

    else:
        raise Exception('Invalid property.')

def handle_oas_component_schemas(schemas):
    # To prevent circular reference,
    # schema should be created breadth-firstly
    for schema_name, schema in schemas.items():
        oas_schema_id = OasSchema.add(schema_name=schema_name)
        schemaNameIdMap[schema_name] = oas_schema_id

    # Then, lazy updated schema's properties
    for schema_name, schema in schemas.items():
        schema_id = schemaNameIdMap.get(schema_name)
        schema = spec.get('components', {}).get('schemas').get(schema_name)
        oas_property_id = handle_oas_property(schema)
        OasSchema.updateById(schema_id, property_id=oas_property_id)

def handle_oas_path(paths):
    for path_name, path in paths.items():
        for operation_name, operation in paths.get(path_name).items():
            request_body = operation.get('requestBody')
            if request_body:
                json_content = request_body.get('content', {}).get('application/json')
                multipart_content = request_body.get('content', {}).get('multipart/form-data')
                if json_content:
                    json_request_body_schema = json_content.get('schema')
                    oas_property_id = handle_oas_property(json_request_body_schema)
                    oas_schema_id = OasSchema.add(property_id=oas_property_id)
                    OasPath.add(platform_id='odhk', oas_path=path_name, oas_operation=operation_name, enable=True, request_body_schema_id=oas_schema_id)
                if multipart_content:
                    print('Multipart is ignored by converter.')

def oas2csv(spec):
    handle_oas_component_schemas(spec.get('components', {}).get('schemas'))
    handle_oas_path(spec.get('paths'))

    OasPath.persist()
    OasSchema.persist()
    OasProperty.persist()
    OasPolymorphicProperty.persist()

with open(args.spec_path) as yaml_file:
    spec = yaml.load(yaml_file, Loader=yaml.FullLoader)
oas2csv(spec)