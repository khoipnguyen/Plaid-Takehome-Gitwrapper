import yaml

class IndentDumper(yaml.Dumper):
    """ Custom class to handle YAML indentation"""
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)

def yaml_dump(yaml_output):
    """Dump the YAML output with custom indentation."""
    return yaml.dump(yaml_output, Dumper=IndentDumper, sort_keys=False)