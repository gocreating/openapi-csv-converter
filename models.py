from Table import Table

OasPath = Table(
    'oas_path',
    'id,platform_id,oas_path,oas_operation,enable,request_body_schema_id'
)
OasSchema = Table(
    'oas_schema',
    'id,schema_name,property_id'
)
OasProperty = Table(
    'oas_property',
    'id,property_name,data_type,nullable,string_format,string_pattern,string_enum,number_format,number_minimum,number_exclusive_minimum,number_maximum,number_exclusive_maximum,number_multiple_of,integer_multiple_of'
)
OasPolymorphicProperty = Table(
    'oas_polymorphic_property',
    'id,property_id,partial_property_id,ref_schema_id'
)