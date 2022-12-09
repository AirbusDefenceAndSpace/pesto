import os
from json import dumps, dump, load
from inspect import getmembers
from importlib.machinery import SourceFileLoader
from pesto.cli.fields import Param, Definition, NATIVES
from pesto.cli.core.utils import PESTO_LOG
from dataclasses import fields, is_dataclass
from pesto.cli.core.pesto_files import PestoFiles

def generate(target:str, force:bool=False):
    module_file=os.path.join(target, "algorithm", "input_output.py") 
    schema_in=os.path.join(target, "pesto", "api", "input_schema.json") 
    schema_out=os.path.join(target, "pesto", "api", "output_schema.json") 
    user_definitions=load(open(os.path.join(target, "pesto", "api", "user_definitions.json")))
    __generate(module_file, schema_in, user_definitions, "Input", force)
    __generate(module_file, schema_out, user_definitions, "Output", force)

def __generate(module_file:str, schema_file:str, user_definitions, class_name:str, force:bool):
    try:
        inout = SourceFileLoader("inout", module_file).load_module()
    except FileNotFoundError:
        PESTO_LOG.error("File {} not found. Can not generate the schemas".format(module_file))
        return
    schema = __class2schema("inout."+class_name, user_definitions, inout, force)
    if schema:
        if os.path.exists(schema_file) and not force:
            PESTO_LOG.warn("Schema file {} already exists. The schema is displayed for information, use --force for overwriting the file.".format(schema_file))
            print(dumps(schema, indent=3))
        else:
            with open(schema_file, 'w') as f:
                dump(schema, f, indent=3)
            PESTO_LOG.info("The {} schema is now in {}".format(class_name, schema_file))

def __class2schema(class_name, user_definitions, inout, force:bool):
    try:
        target_class=eval(class_name)
        if not is_dataclass(target_class):
            PESTO_LOG.error("Class {} is not a dataclass (decorated with @dataclass annotation). Can not generate the schemas for this class".format(class_name))
            return
    except AttributeError as err:
        PESTO_LOG.error("Class {} not found. Can not generate the schemas".format(class_name))
        PESTO_LOG.exception(err)
        return
    schema={}
    required=[]
    for f in fields(target_class):
        field_type = f.type
        if Param.type in f.metadata:
            field_type =f.metadata[Param.type]
        if Param.required in f.metadata and f.metadata[Param.required]:
            required.append(f.name)
        if field_type in NATIVES.keys():
            schema[f.name]={"type":NATIVES[field_type]}
        else:
            if isinstance(field_type, Definition) and field_type.value in [t.value for t in Definition]:
                schema[f.name]={"$ref":"#/definitions/"+field_type.name}
            else:
                if field_type in user_definitions:
                    PESTO_LOG.info("Using the {} user defined definition from {}".format(field_type, PestoFiles.user_definitions_schema))
                    schema[f.name]=user_definitions[field_type]
                else:
                    PESTO_LOG.error("The {} type of {} is not native, is not a pesto definition and is not found in the user defined definitions from {}".format(field_type, f.name, PestoFiles.user_definitions_schema))
                    raise ValueError('Invalid definition {} for {}'.format(field_type, f.name))
        if Param.description in f.metadata:
           schema[f.name]["description"]=f.metadata[Param.description].strip()
    schema["required"]=required
    return schema
