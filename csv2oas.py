import yaml

from models import OasPath, OasSchema, OasProperty, OasPolymorphicProperty

spec = {}

def property_id_to_spec(property_id):
    oas_property = OasProperty.findDictById(property_id)
    oas_property_type = oas_property.get('data_type')
    property_spec = {}

    if oas_property_type == 'string':
        property_spec['type'] = 'string'
        return property_spec

    elif oas_property_type == 'number':
        property_spec['type'] = 'number'
        return property_spec

    elif oas_property_type == 'integer':
        property_spec['type'] = 'integer'
        return property_spec

    elif oas_property_type == 'boolean':
        property_spec['type'] = 'boolean'
        return property_spec

    elif oas_property_type == 'array':
        property_spec['type'] = 'array'
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            property_spec['items'] = property_id_to_spec(oas_polymorphic_property.get('partial_property_id'))
        return property_spec

    elif oas_property_type == 'object':
        property_spec['type'] = 'object'
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        property_spec['properties'] = {}
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            partial_property = OasProperty.findDictById(partial_property_id)
            property_spec['properties'][partial_property.get('property_name')] = property_id_to_spec(partial_property_id)
        return property_spec

    elif oas_property_type == 'oneOf':
        property_spec['oneOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['oneOf'].append(property_id_to_spec(partial_property_id))
        return property_spec

    elif oas_property_type == 'anyOf':
        property_spec['anyOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['anyOf'].append(property_id_to_spec(partial_property_id))
        return property_spec

    elif oas_property_type == 'allOf':
        property_spec['allOf'] = []
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        for oas_polymorphic_property in oas_polymorphic_properties:
            partial_property_id = oas_polymorphic_property.get('partial_property_id')
            property_spec['allOf'].append(property_id_to_spec(partial_property_id))
        return property_spec

    elif oas_property_type == '$ref':
        oas_polymorphic_properties = OasPolymorphicProperty.findDict(property_id=oas_property.get('id'))
        ref_schema_id = oas_polymorphic_properties[0].get('ref_schema_id')
        ref_schema = OasSchema.findDictById(ref_schema_id)
        ref_schema_name = ref_schema.get('schema_name')
        property_spec['$ref'] = f'#/components/schemas/{ref_schema_name}'
        return property_spec

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
