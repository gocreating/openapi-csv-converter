import yaml
import unittest

class TestConversion(unittest.TestCase):
    maxDiff = None

    def test_conversion(self):
        with open('./sample/source-oas.yaml') as yaml_file:
            raw_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)
        with open('./build/oas.yaml') as yaml_file:
            converted_spec = yaml.load(yaml_file, Loader=yaml.FullLoader)

        # Asset components.schemas
        self.assertDictEqual(raw_spec['components']['schemas'], converted_spec['components']['schemas'])

        # Assert `requestBody` only (responses are not supported yet)
        for path_name, path in raw_spec['paths'].items():
            for operation_name, operation in raw_spec['paths'][path_name].items():
                self.assertDictEqual(
                    raw_spec['paths'][path_name][operation_name]['requestBody'],
                    converted_spec['paths'][path_name][operation_name]['requestBody']
                )