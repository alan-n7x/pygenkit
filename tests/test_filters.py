import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pygenkit.utils.filters import TemplateFilters  # noqa: E402


def test_snake_case() -> None:
    assert TemplateFilters.snake_case("hello-world") == "hello_world"
    assert TemplateFilters.snake_case("Hello World") == "hello_world"
    assert TemplateFilters.snake_case("hello_world") == "hello_world"


def test_kebab_case() -> None:
    assert TemplateFilters.kebab_case("hello_world") == "hello-world"
    assert TemplateFilters.kebab_case("Hello World") == "hello-world"


def test_pascal_case() -> None:
    assert TemplateFilters.pascal_case("hello-world") == "HelloWorld"
    assert TemplateFilters.pascal_case("hello_world") == "HelloWorld"


def test_camel_case() -> None:
    assert TemplateFilters.camel_case("hello-world") == "helloWorld"
    assert TemplateFilters.camel_case("Hello-World") == "helloWorld"


def test_module_name() -> None:
    assert TemplateFilters.module_name("hello-world") == "hello_world"
