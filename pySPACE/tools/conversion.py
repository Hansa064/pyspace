""" Type conversion helper functions """
import copy
import warnings
import yaml


def python2yaml(value):
    """ Conversion function to handle yaml specialties"""
    # due to ugly incompatibilities in the conversion of
    # float (yaml) -> float (python) -> float(yaml) and
    # iterable(python) -> iterable(yaml),
    # we have to introduce this special treatment
    str_representation = yaml.dump([value], default_flow_style=True).strip()
    if str_representation.startswith('-'):
        return str_representation[2:]
    elif str_representation.startswith('['):
        return str_representation[1:-1]
    else:
        warnings.warn("Wrong format for yaml conversion of template (%s)."
                      % str_representation)
        return str(value)


def extract_key_str(full_file, keyword="node_chain"):
    """ Extract the string which corresponds to the specified YAML key

    For extraction it is assumed, that a line wise notation is used,
    which begins with the keyword.
    """
    lines = full_file.split("\n")
    keyword_found = False
    keyword_lines = []
    for line in lines:
        if keyword_found:
            short = line.strip()
            if short == "" or short.startswith("#"):
                continue
            elif line.startswith(" "):  # indentation occurred
                keyword_lines.append(line)
            elif ":" in line:  # next keyword occurred
                break
            else:
                warnings.warn("Unexpected line occurred: %s!"%line)
                keyword_lines.append(line)
        elif line.startswith(keyword):
            keyword_found = True
    return "\n".join(keyword_lines)


def replace_parameters_and_convert(node_chain_spec, parameter_setting):
    """ Replace parameters of parameter_setting in node_chain_spec

    and return the Python object and not the YAML string.
    """
    # we have not specified a template file but a complete
    # node chain instead, for replacing parameters, it has to be reconverted
    # to a string
    if type(node_chain_spec) == list:
        node_chain_spec = repr(node_chain_spec)  #yaml.dump(node_chain_spec)
        warnings.warn("Issues with parameter replacement might occur!")
    elif isinstance(node_chain_spec, basestring):
        pass
    else:
        warnings.warn("Wrong format of template (%s). Trying to proceed."
                      % str(node_chain_spec))
    node_chain_spec = replace_parameters(node_chain_spec, parameter_setting)
    # final loading of the modified YAML file
    return yaml.load(node_chain_spec)


def replace_parameters(node_chain_spec, parameter_setting):
    """ Replace parameters in string and return this string """
    # Instantiate the template
    for key, value in parameter_setting.iteritems():
        # Parameters framed by "#" are considered to be escaped
        if "#"+key+"#" in node_chain_spec:
            node_chain_spec = node_chain_spec.replace("#"+key+"#", "##")
        #chek for optimization and normal parameter rule
        elif key.startswith("_") or key.startswith("~"):
            try:
                if type(value) == str:
                    node_chain_spec = \
                        node_chain_spec.replace("%s" % str(key), value)
                else:
                    node_chain_spec = node_chain_spec.replace(
                        "%s" % str(key), repr(value))
            except:
                node_chain_spec = node_chain_spec.replace(
                    "%s" % str(key), python2yaml(value))
        else:
            node_chain_spec = node_chain_spec.replace(
                "%s" % str(key), python2yaml(value))
            warnings.warn("The parameter %s is no regular parameter." +
                          "Better use one starting with '_' or '~'. " +
                          "Replacing despite." % key)
        if "##" in node_chain_spec:
            node_chain_spec = node_chain_spec.replace("##", key)
    return node_chain_spec


def replace_in_list(list_, name, replacement):
    for idx, item in enumerate(list_):
        # Base case: item is not a structure
        if item == name:
            list_[idx] = replacement
        # The item is itself a list, replace recursivly
        if isinstance(item, list):
            # Check recursively
            list_[idx] = replace_in_list(item, name, replacement)
        # The item is a dict, look for keys and values
        elif isinstance(item, dict):
            list_[idx] = replace_in_dict(item, name, replacement)
    return list_


def replace_in_dict(dict_, name, replacement):
    new_dict = copy.copy(dict_)
    for key, value in dict_.iteritems():
        if key == name:
            del new_dict[key]
            new_dict[replacement] = value
        if value == name:
            new_dict[key] = replacement
        if isinstance(value, list):
            new_dict[key] = replace_in_list(value, name, replacement)
        elif isinstance(value, dict):
            new_dict[key] = replace_in_dict(value, name, replacement)
    return new_dict


def replace_parameters2(node_chain_spec, parameter_setting):
    for key, value in parameter_setting.iteritems():
        node_chain_spec = replace_in_list(node_chain_spec, "#"+key+"#", "##")
        #chek for optimization and normal parameter rule
        if not key.startswith("_") and not key.startswith("~"):
            warnings.warn("The parameter %s is no regular parameter." +
                          "Better use one starting with '_' or '~'. " +
                          "Replacing despite." % key)
        node_chain_spec = replace_in_list(node_chain_spec, key, value)
        node_chain_spec = replace_in_list(node_chain_spec, "##", key)
    return node_chain_spec
