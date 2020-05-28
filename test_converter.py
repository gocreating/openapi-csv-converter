import os
import yaml
import unittest
import jsonschema

class ConverterTest(unittest.TestCase):
    maxDiff = None
    S1 = os.environ.get('S1')
    S2 = os.environ.get('S2')

    def __init__(self, *args, **kwargs):
        super(ConverterTest, self).__init__(*args, **kwargs)
        with open(self.S1) as yaml_file:
            self.raw_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)
        with open(self.S2) as yaml_file:
            self.converted_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)

    def test_json_schema(self):
        # Assert both source schema and converted schema are valid jsonschema format
        for schema_name, schema_spec in self.raw_spec['components']['schemas'].items():
            jsonschema.Draft7Validator.check_schema(schema_spec)
            jsonschema.Draft7Validator.check_schema(self.converted_spec['components']['schemas'][schema_name])

        for path_name, path in self.raw_spec['paths'].items():
            for operation_name, operation in self.raw_spec['paths'][path_name].items():
                raw_schema = operation.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
                converted_schema = self.converted_spec['paths'][path_name][operation_name].get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
                if raw_schema:
                    jsonschema.Draft7Validator.check_schema(raw_schema)
                    jsonschema.Draft7Validator.check_schema(converted_schema)

    def test_converter(self):
        # Asset components.schemas
        for schema_name, schema_spec in self.raw_spec['components']['schemas'].items():
            self.assertDictEqual(schema_spec, self.converted_spec['components']['schemas'][schema_name])

        # Assert `requestBody` only (responses are not supported yet)
        for path_name, path in self.raw_spec['paths'].items():
            for operation_name, operation in self.raw_spec['paths'][path_name].items():
                self.assertDictEqual(
                    self.raw_spec['paths'][path_name][operation_name]['requestBody'],
                    self.converted_spec['paths'][path_name][operation_name]['requestBody']
                )