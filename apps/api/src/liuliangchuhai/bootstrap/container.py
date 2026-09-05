from dataclasses import dataclass
from importlib.resources import as_file, files

from liuliangchuhai.application.ports.assistant import AssistantPort
from liuliangchuhai.application.ports.content_planner import ContentPlannerPort
from liuliangchuhai.application.ports.digital_human import DigitalHumanPort
from liuliangchuhai.application.ports.llm import LLMPort
from liuliangchuhai.application.ports.product_repository import ProductRepository
from liuliangchuhai.application.use_cases.analyze_product import AnalyzeProductUseCase
from liuliangchuhai.application.use_cases.analyze_product_by_id import AnalyzeProductByIdUseCase
from liuliangchuhai.application.use_cases.create_content_plan import CreateContentPlanUseCase
from liuliangchuhai.application.use_cases.create_content_plan_by_id import (
    CreateContentPlanByIdUseCase,
)
from liuliangchuhai.application.use_cases.generate_digital_human import GenerateDigitalHumanUseCase
from liuliangchuhai.application.use_cases.get_product import GetProduct
from liuliangchuhai.application.use_cases.get_system_status import GetSystemStatus
from liuliangchuhai.application.use_cases.list_products import ListProducts
from liuliangchuhai.application.use_cases.reply_to_customer import ReplyToCustomer
from liuliangchuhai.bootstrap.settings import Settings
from liuliangchuhai.infrastructure.assistant.deepseek import DeepSeekAssistantAdapter
from liuliangchuhai.infrastructure.assistant.mock import MockAssistantAdapter
from liuliangchuhai.infrastructure.content.deepseek import DeepSeekContentPlannerAdapter
from liuliangchuhai.infrastructure.content.mock import MockContentPlannerAdapter
from liuliangchuhai.infrastructure.digital_human.mock import MockDigitalHumanAdapter
from liuliangchuhai.infrastructure.llm.deepseek import DeepSeekLLMAdapter
from liuliangchuhai.infrastructure.llm.mock import MockLLMAdapter
from liuliangchuhai.infrastructure.products.json_repository import JsonProductRepository


@dataclass(frozen=True, slots=True)
class Container:
    assistant: AssistantPort
    reply_to_customer: ReplyToCustomer
    llm: LLMPort
    content_planner: ContentPlannerPort
    create_content_plan: CreateContentPlanUseCase
    create_content_plan_by_id: CreateContentPlanByIdUseCase
    digital_human: DigitalHumanPort
    generate_digital_human: GenerateDigitalHumanUseCase
    get_system_status: GetSystemStatus
    product_repository: ProductRepository
    list_products: ListProducts
    get_product: GetProduct
    analyze_product: AnalyzeProductUseCase
    analyze_product_by_id: AnalyzeProductByIdUseCase


def _build_llm(settings: Settings) -> LLMPort:
    if settings.llm_provider == "mock":
        return MockLLMAdapter()
    if settings.llm_provider == "deepseek":
        assert settings.deepseek_api_key is not None
        return DeepSeekLLMAdapter(
            api_key=settings.deepseek_api_key.get_secret_value(),
            model=settings.deepseek_model,
            timeout_seconds=settings.deepseek_timeout_seconds,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider!r}")


def _build_assistant(settings: Settings) -> AssistantPort:
    if settings.assistant_provider == "mock":
        return MockAssistantAdapter()
    if settings.assistant_provider == "deepseek":
        assert settings.deepseek_api_key is not None
        return DeepSeekAssistantAdapter(
            api_key=settings.deepseek_api_key.get_secret_value(),
            model=settings.deepseek_model,
            timeout_seconds=settings.deepseek_timeout_seconds,
        )
    raise ValueError(f"Unsupported assistant provider: {settings.assistant_provider!r}")


def _build_content_planner(settings: Settings) -> ContentPlannerPort:
    if settings.llm_provider == "mock":
        return MockContentPlannerAdapter()
    if settings.llm_provider == "deepseek":
        assert settings.deepseek_api_key is not None
        return DeepSeekContentPlannerAdapter(
            api_key=settings.deepseek_api_key.get_secret_value(),
            model=settings.deepseek_model,
            timeout_seconds=settings.deepseek_timeout_seconds,
        )
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider!r}")


def _build_digital_human(provider: str) -> DigitalHumanPort:
    if provider == "mock":
        return MockDigitalHumanAdapter()
    raise ValueError(f"Unsupported digital-human provider: {provider!r}")


def build_container(settings: Settings) -> Container:
    llm = _build_llm(settings)
    digital_human = _build_digital_human(settings.digital_human_provider)
    catalog = files("liuliangchuhai.infrastructure.products").joinpath("demo_products.json")
    with as_file(catalog) as path:
        product_repository = JsonProductRepository(path)
    get_product = GetProduct(product_repository)
    analyze_product = AnalyzeProductUseCase(llm)
    content_planner = _build_content_planner(settings)
    create_content_plan = CreateContentPlanUseCase(content_planner)
    assistant = _build_assistant(settings)
    return Container(
        assistant=assistant,
        reply_to_customer=ReplyToCustomer(get_product, assistant),
        content_planner=content_planner,
        create_content_plan=create_content_plan,
        create_content_plan_by_id=CreateContentPlanByIdUseCase(get_product, create_content_plan),
        llm=llm,
        digital_human=digital_human,
        generate_digital_human=GenerateDigitalHumanUseCase(digital_human),
        get_system_status=GetSystemStatus(llm=llm, digital_human=digital_human),
        product_repository=product_repository,
        list_products=ListProducts(product_repository),
        get_product=get_product,
        analyze_product=analyze_product,
        analyze_product_by_id=AnalyzeProductByIdUseCase(get_product, analyze_product),
    )
