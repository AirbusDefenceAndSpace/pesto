import os
from json import dumps, dump
from inspect import getmembers
from importlib.machinery import SourceFileLoader
from pesto.cli.fields import Param, Definition, NATIVES
from pesto.cli.core.utils import PESTO_LOG
from dataclasses import fields, is_dataclass

def generate(class_file:str, schema_in:str, schema_out:str, force:bool=False):
    __generate(class_file, schema_in, "Input", force)
    __generate(class_file, schema_out, "Output", force)

def __generate(class_file:str, schema_file:str, class_name:str, force:bool):
    try:
        inout = SourceFileLoader("inout", class_file).load_module()
    except FileNotFoundError:
        PESTO_LOG.error("File {} not found. Can not generate the schemas".format(class_file))
        return
    schema = __instance2schema("inout."+class_name, inout, force)
    if schema:
        if os.path.exists(schema_file) and not force:
            PESTO_LOG.warn("Schema file {} already exists. The schema is displayed for information, use --force for overwriting the file.".format(schema_file))
            print(dumps(schema, indent=3))
        else:
            with open(schema_file, 'w') as f:
                dump(schema, f, indent=3)
            PESTO_LOG.info("The {} schema is now in {}".format(class_name, schema_file))

def __instance2schema(class_name, inout, force:bool):
    try:
        instance=eval(class_name)()
        if not is_dataclass(instance):
            PESTO_LOG.error("Class {} is not a dataclass (decorated with @dataclass annotation). Can not generate the schemas for this class".format(class_name))
            return
    except AttributeError as err:
        PESTO_LOG.error("Class {} not found. Can not generate the schemas".format(class_name))
        PESTO_LOG.exception(err)
        return
    schema={}
    required=[]
    for f in fields(instance):
        field_type = f.type
        if Param.type in f.metadata:
            field_type =f.metadata[Param.type]
        if Param.required in f.metadata:
            required.append(f.name)
        if field_type in NATIVES.keys():
            schema[f.name]={"type":NATIVES[field_type]}
        else:
            if isinstance(field_type, Definition) and field_type.value in [t.value for t in Definition]:
                schema[f.name]={"$ref":"#/definitions/"+field_type.name}
            else:
                PESTO_LOG.error("Type {} not supported for field in {}. Can not generate the schemas".format(field_type, f.name))
                raise ValueError("Type {} not supported for field in {}".format(field_type, f.name))
        if Param.description in f.metadata:
           schema[f.name]["description"]=f.metadata[Param.description].strip()
    schema["required"]=required
    return schema
