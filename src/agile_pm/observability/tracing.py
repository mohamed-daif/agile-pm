"""OpenTelemetry tracing configuration."""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
import os

def setup_tracing(service_name: str = "agile-pm"):
    """Configure OpenTelemetry tracing."""
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    otlp_endpoint = os.getenv("OTLP_ENDPOINT", "localhost:4317")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

def instrument_fastapi(app):
    """Instrument FastAPI app."""
    FastAPIInstrumentor.instrument_app(app)

tracer = None

def get_tracer():
    global tracer
    if tracer is None:
        tracer = setup_tracing()
    return tracer
