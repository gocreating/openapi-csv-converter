def str2bool(s):
    return s.lower() in ('true',)

def ref2schema_name(ref_str):
    return ref_str.replace('#/components/schemas/', '')

def schema_name2ref(schema_name):
    return f'#/components/schemas/{schema_name}'
