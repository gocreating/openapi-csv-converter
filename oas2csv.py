import yaml

from argparse import ArgumentParser
from models import OasPath, OasSchema, OasProperty, OasPolymorphicProperty

parser = ArgumentParser()
parser.add_argument("-s", "--spec-file", dest="spec_path")
args = parser.parse_args()

schemaNameIdMap = {}

def handle_oas_property(oas_property, oas_property_name=None):
    oas_property_type = oas_property.get('type')

    if oas_property_type == 'string':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='string')
        return oas_property_id

    elif oas_property_type == 'number':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='number')
        return oas_property_id

    elif oas_property_type == 'integer':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='integer')
        return oas_property_id

    elif oas_property_type == 'boolean':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='boolean')
        return oas_property_id

    elif oas_property_type == 'array':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='array')
        prop = oas_property.get('items')
        partial_property_id = handle_oas_property(prop)
        OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property_type == 'object':
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='object')
        for prop_name, prop in oas_property.get('properties').items():
            partial_property_id = handle_oas_property(prop, prop_name)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('oneOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='oneOf')
        for prop in oas_property.get('oneOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('anyOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='anyOf')
        for prop in oas_property.get('anyOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('allOf'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='allOf')
        for prop in oas_property.get('allOf'):
            partial_property_id = handle_oas_property(prop)
            OasPolymorphicProperty.add(property_id=oas_property_id, partial_property_id=partial_property_id)
        return oas_property_id

    elif oas_property.get('$ref'):
        oas_property_id = OasProperty.add(property_name=oas_property_name, data_type='$ref')
        schemaName = oas_property.get('$ref').replace('#/components/schemas/', '')
        OasPolymorphicProperty.add(property_id=oas_property_id, ref_schema_id=schemaNameIdMap.get(schemaName))
        return oas_property_id

    else:
        raise Exception('Invalid property.')

def handle_oas_component_schema(schemas):
    for schema_name, schema in schemas.items():
        oas_property_id = handle_oas_property(schema)
        oas_schema_id = OasSchema.add(schema_name=schema_name, property_id=oas_property_id)
        schemaNameIdMap[schema_name] = oas_schema_id

def handle_oas_path(paths):
    for path_name, path in paths.items():
        for operation_name, operation in paths.get(path_name).items():
            json_request_body_schema = operation.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
            oas_property_id = handle_oas_property(json_request_body_schema)
            oas_schema_id = OasSchema.add(property_id=oas_property_id)
            OasPath.add(platform_id='odhk', oas_path=path_name, oas_operation=operation_name, enable=True, request_body_schema_id=oas_schema_id)

def oas2csv(spec):
    handle_oas_component_schema(spec.get('components', {}).get('schemas'))
    handle_oas_path(spec.get('paths'))

    OasPath.persist()
    OasSchema.persist()
    OasProperty.persist()
    OasPolymorphicProperty.persist()

with open(args.spec_path) as yaml_file:
    spec = yaml.load(yaml_file, Loader=yaml.FullLoader)
oas2csv(spec)