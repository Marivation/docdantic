from typing import Union, List, Dict, Literal
from types import UnionType
from markdown import Markdown
from pydantic import BaseModel, Field

from docdantic import (
    PydanticUndefined,
    is_pydantic_model,
    get_default_string,
    get_annotation_string,
    import_class,
    get_field_info,
    submodel_link,
    highlight_name,
    extract_configuration,
    render_table,
    process_line,
    DocdanticPreprocessor,
    is_typing_literal,
    is_typing_union,
    is_typing_list,
    is_typing_dict
)

def test_type_checks() -> None:
    literal = Literal['tmp']
    union = Union[int, float]
    array = List[str]
    dictionary = Dict[str, float]

    assert is_typing_literal(literal) is True
    assert is_typing_literal(union) is False
    assert is_typing_literal(array) is False
    assert is_typing_literal(dictionary) is False

    assert is_typing_union(union) is True
    assert is_typing_union(literal) is False
    assert is_typing_union(array) is False
    assert is_typing_union(dictionary) is False

    assert is_typing_list(array) is True
    assert is_typing_list(literal) is False
    assert is_typing_list(union) is False
    assert is_typing_list(dictionary) is False

    assert is_typing_dict(dictionary) is True
    assert is_typing_dict(literal) is False
    assert is_typing_dict(union) is False
    assert is_typing_dict(array) is False


# Test the is_pydantic_model function
def test_is_pydantic_model() -> None:
    class Model(BaseModel):
        pass

    assert is_pydantic_model(Model) is True
    assert is_pydantic_model(list) is False
    assert is_pydantic_model(None) is False


# Test the get_default_string function
def test_get_default_string() -> None:
    field_undefined = PydanticUndefined
    field_with_default = 'test_default'

    assert get_default_string(field_undefined) == "..."
    assert get_default_string(field_with_default) == 'test_default'


# Test the get_annotation_string function
def test_get_annotation_string() -> None:
    assert get_annotation_string(None) == "None"
    assert get_annotation_string(int) == 'int'
    assert get_annotation_string(str) == 'str'
    assert get_annotation_string(List[str]) == 'List[str]'
    assert get_annotation_string(Dict[str, int]) == 'Dict[str, int]'
    assert get_annotation_string(bool) == 'bool'
    assert get_annotation_string(float) == 'float'
    assert get_annotation_string(Union[float, int]) == 'Union[float, int]'


# Test the import_class function
def test_import_class() -> None:
    assert import_class('docdantic.ModelFieldInfo') is not None
    assert import_class('non_existent_module.NonExistentClass') is None


# Test the get_field_info function
def test_get_field_info() -> None:
    class DummyModel(BaseModel):
        field: int = 1

    info = get_field_info(DummyModel)
    assert len(info) == 1
    assert 'DummyModel' in info
    assert len(info['DummyModel']) == 2
    assert info['DummyModel'][0] is None # no documentation
    assert info['DummyModel'][1][0].name == '**field**'
    assert info['DummyModel'][1][0].type == 'int'
    assert info['DummyModel'][1][0].required == 'False'
    assert info['DummyModel'][1][0].default == '1'
    assert info['DummyModel'][1][0].description == '' # no field documentation

    class DummyCollectionModel(BaseModel):
        field: List[DummyModel] = []

    info = get_field_info(DummyCollectionModel)
    assert len(info) == 2
    assert 'DummyModel' in info
    assert len(info['DummyCollectionModel']) == 2
    assert info['DummyCollectionModel'][0] is None # no documentation
    assert info['DummyCollectionModel'][1][0].name == '**field**'
    assert info['DummyCollectionModel'][1][0].type == 'List[[DummyModel](#dummymodel)]'
    assert info['DummyCollectionModel'][1][0].required == 'False'
    assert info['DummyCollectionModel'][1][0].default == '[]'
    assert info['DummyCollectionModel'][1][0].description == '' # no field documentation

# Test submodel_link function
def test_submodel_link():
    assert submodel_link('DummyModel') == '[DummyModel](#dummymodel)'

# Test highlight_name function
def test_highlight_name():
    assert highlight_name('field_name') == '**field_name**'

# Test extract_configuration function
def test_extract_configuration():
    lines = ["!docdantic: tests.test_docdantic.DummyModel", "  {\"exclude\": {\"DummyModel\": [\"field\"]}}"]
    config, index = extract_configuration(0, lines)
    assert config == {"exclude": {"DummyModel": ["field"]}}
    assert index == 2

class DummyModel(BaseModel):
    field: int = Field(default=1)

# Test render_table function
def test_render_table():
    table = render_table('tests.test_docdantic.DummyModel', {})
    assert all(item in table for item in ["**field**", "int", "False", "1"]) 

# Test process_line function
def test_process_line():
    lines = ["!docdantic: tests.test_docdantic.DummyModel", "  {\"exclude\": {\"DummyModel\": [\"field\"]}}"]
    processed_line, index = process_line(0, lines)
    assert all(item not in processed_line for item in ["**field**", "int", "False", "1"]) 
    assert index == 2

# Test DocdanticPreprocessor
def test_DocdanticPreprocessor():
    markdown = Markdown(extensions=[])
    preprocessor = DocdanticPreprocessor(markdown)
    lines = ["!docdantic: tests.test_docdantic.DummyModel", "  {\"exclude\": {\"DummyModel\": [\"field\"]}}"]
    parsed_lines = preprocessor.run(lines)
    assert all(item not in line for item in ["**field**", "int", "False", "1"] for line in parsed_lines) 
