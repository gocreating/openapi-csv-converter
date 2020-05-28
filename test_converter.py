import os
import yaml
import unittest

class TestConverter(unittest.TestCase):
    maxDiff = None
    S1 = os.environ.get('S1')
    S2 = os.environ.get('S2')

    def test_converter(self):
        with open(self.S1) as yaml_file:
            raw_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)
        with open(self.S2) as yaml_file:
            converted_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)

        # Asset components.schemas
        for schema_name, schema_spec in raw_spec['components']['schemas'].items():
            self.assertDictEqual(schema_spec, converted_spec['components']['schemas'][schema_name])

        # Assert `requestBody` only (responses are not supported yet)
        for path_name, path in raw_spec['paths'].items():
            for operation_name, operation in raw_spec['paths'][path_name].items():
                self.assertDictEqual(
                    raw_spec['paths'][path_name][operation_name]['requestBody'],
                    converted_spec['paths'][path_name][operation_name]['requestBody']
                )