from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.httpx import HttpxInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_tracer(service_name: str):
    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({"service.name": service_name}))
    )
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",
        agent_port=6831,
    )
    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

    HttpxInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
