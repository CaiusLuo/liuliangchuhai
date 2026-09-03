from dataclasses import dataclass
from importlib.resources import as_file, files

from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.application.use_cases.get_product import GetProduct
from liuliangchuhai.application.use_cases.get_system_status import GetSystemStatus
from liuliangchuhai.application.use_cases.list_products import ListProducts
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter
from liuliangchuhai.infrastructure.products.json_repository import JsonProductRepository


@dataclass(frozen=True, slots=True)
class Container:
    llm: LLMPort
    digital_human: DigitalHumanPort
    get_system_status: GetSystemStatus
    product_repository: ProductRepository
    list_products: ListProducts
    get_product: GetProduct


def _build_llm(provider: str) -> LLMPort:
    if provider == "mock":
        return MockLLMAdapter()
    raise ValueError(f"Unsupported LLM provider: {provider!r}")


def _build_digital_human(provider: str) -> DigitalHumanPort:
    if provider == "mock":
        return MockDigitalHumanAdapter()
    raise ValueError(f"Unsupported digital-human provider: {provider!r}")


def build_container(settings: Settings) -> Container:
    llm = _build_llm(settings.llm_provider)
    digital_human = _build_digital_human(settings.digital_human_provider)
    catalog = files("liuliangchuhai.infrastructure.products").joinpath("demo_products.json")
    with as_file(catalog) as path:
        product_repository = JsonProductRepository(path)
    return Container(
        llm=llm,
        digital_human=digital_human,
        get_system_status=GetSystemStatus(llm=llm, digital_human=digital_human),
        product_repository=product_repository,
        list_products=ListProducts(product_repository),
        get_product=GetProduct(product_repository),
    )
