import json
import os
from typing import Any, Dict, Callable, List, Union

from pesto.ws.features.converter.image.image import Image


class PathLoader:
    def match(self, file_path: str) -> bool:
        raise NotImplementedError()

    def load(self, file_path: str) -> Any:
        raise NotImplementedError()


# DEFAULT (URI based) loader ################################################


class UriLoader(PathLoader):
    def __init__(self, file_prefix: str):
        self.file_prefix = file_prefix

    def match(self, file_path: str) -> bool:
        return True

    def load(self, file_path: str) -> Any:
        return "{}{}".format(self.file_prefix, file_path)


# Recursive (FOLDER) loader #################################################


class FolderLoader(PathLoader):
    def __init__(self, global_loader: Callable[[str], Any]) -> None:
        self.loader = global_loader

    def match(self, file_path: str) -> bool:
        return os.path.isdir(file_path)

    def load(self, file_path: str) -> Union[Dict, List]:
        is_array = all([os.path.splitext(x)[0].isdigit() for x in os.listdir(file_path)])

        if is_array:
            return [self.loader(os.path.join(file_path, x)) for x in sorted(os.listdir(file_path))]
        else:
            return {
                os.path.splitext(x)[0]: self.loader(os.path.join(file_path, x))
                for x in sorted(os.listdir(file_path))
            }


# Specific FILE loaders ####################################################


class FileLoader(PathLoader):
    def __init__(self, *args: str):
        self.extension_pattern: [str] = [arg.lower() for arg in args]

    @staticmethod
    def _match(file_path, extension_pattern):
        return file_path.lower().endswith(extension_pattern)

    def match(self, file_path: str) -> bool:
        return any([self._match(file_path, ext) for ext in self.extension_pattern])

    def load(self, file_path: str) -> Any:
        raise NotImplementedError()


class Base64ImageLoader(FileLoader):
    def load(self, file_path: str) -> str:
        image = Image.from_uri(file_path)
        return image.to_base64()


class StringLoader(FileLoader):
    def load(self, file_path: str) -> str:
        with open(file_path) as _:
            return str(_.read())


class FloatLoader(FileLoader):
    def load(self, file_path: str) -> float:
        with open(file_path) as _:
            return float(_.read())


class IntLoader(FileLoader):
    def load(self, file_path: str) -> int:
        with open(file_path) as _:
            return int(_.read())


class JsonLoader(FileLoader):
    def load(self, file_path: str) -> Any:
        with open(file_path) as _:
            return json.load(_)


# Generic loader based on delegation to a sequence of loaders ##############


class GenericLoader(PathLoader):
    def __init__(self) -> None:
        self.loaders: List[PathLoader] = []

    def set_loaders(self, loaders: List[PathLoader]) -> None:
        self.loaders = loaders

    def match(self, file_path: str) -> bool:
        return True

    def load(self, file_path: str) -> Any:
        for loader in self.loaders:
            if loader.match(file_path):
                return loader.load(file_path)

        raise ValueError("Unsupported file path: {}".format(file_path))


# Payload Generator


class PayloadGenerator:
    def __init__(self, file_prefix: str = "file://", images_as_base64=False):
        self.loader = GenericLoader()

        # default loaders
        loaders = [
            FolderLoader(self.loader.load),
            StringLoader(".string"),
            FloatLoader(".float", ".number"),
            IntLoader(".int", ".integer"),
            JsonLoader(".json", ".geojson"),
        ]

        # base64 images parsing
        if images_as_base64:
            loaders.append(Base64ImageLoader(".tif", ".jpg", ".png", ".tiff", ".jpeg"))

        # default loading is local uri file://
        loaders.append(UriLoader(file_prefix))

        self.loader.set_loaders(loaders)

    def generate(self, path: str) -> Any:
        path = os.path.abspath(path)
        print("path={}".format(path))
        result = self.loader.load(path)
        if len(result) == 0:
            return dict()
        return result
