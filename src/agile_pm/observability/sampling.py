"""Trace sampling configuration."""
from typing import Optional
from opentelemetry.sdk.trace.sampling import (
    Sampler,
    SamplingResult,
    Decision,
    ParentBased,
    TraceIdRatioBased,
    ALWAYS_ON,
    ALWAYS_OFF,
)
from opentelemetry.trace import SpanKind, Link
from opentelemetry.util.types import Attributes
from opentelemetry.context import Context

from agile_pm.core.config import settings


class AdaptiveSampler(Sampler):
    """Adaptive sampler based on span attributes."""
    
    def __init__(
        self,
        default_rate: float = 0.1,
        error_rate: float = 1.0,
        slow_threshold_ms: float = 1000,
    ):
        self.default_rate = default_rate
        self.error_rate = error_rate
        self.slow_threshold_ms = slow_threshold_ms
        self._ratio_sampler = TraceIdRatioBased(default_rate)
    
    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Attributes] = None,
        links: Optional[Link] = None,
    ) -> SamplingResult:
        """Determine if span should be sampled."""
        attributes = attributes or {}
        
        # Always sample errors
        if attributes.get("error") or attributes.get("http.status_code", 200) >= 500:
            return SamplingResult(Decision.RECORD_AND_SAMPLE, attributes)
        
        # Always sample health check endpoints at lower rate
        if name.startswith("/health") or name.startswith("/ready"):
            if TraceIdRatioBased(0.01).should_sample(
                parent_context, trace_id, name, kind, attributes, links
            ).decision == Decision.RECORD_AND_SAMPLE:
                return SamplingResult(Decision.RECORD_AND_SAMPLE, attributes)
            return SamplingResult(Decision.DROP, attributes)
        
        # Use default ratio for normal requests
        return self._ratio_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links
        )
    
    def get_description(self) -> str:
        return f"AdaptiveSampler(default={self.default_rate}, error={self.error_rate})"


class TailBasedSampler(Sampler):
    """
    Tail-based sampling stub.
    In production, this would buffer spans and make decisions after the trace completes.
    """
    
    def __init__(self, rate: float = 0.1):
        self.rate = rate
        self._ratio_sampler = TraceIdRatioBased(rate)
    
    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: Optional[SpanKind] = None,
        attributes: Optional[Attributes] = None,
        links: Optional[Link] = None,
    ) -> SamplingResult:
        """
        For true tail-based sampling, you'd use an external collector
        like Jaeger or OpenTelemetry Collector with tail sampling processor.
        This is a simplified head-based fallback.
        """
        return self._ratio_sampler.should_sample(
            parent_context, trace_id, name, kind, attributes, links
        )
    
    def get_description(self) -> str:
        return f"TailBasedSampler(rate={self.rate})"


def get_sampler() -> Sampler:
    """Get configured sampler based on settings."""
    sampling_config = getattr(settings, "tracing_sampling", {})
    
    strategy = sampling_config.get("strategy", "parent_based")
    rate = sampling_config.get("rate", 0.1)
    
    if strategy == "always_on":
        return ALWAYS_ON
    elif strategy == "always_off":
        return ALWAYS_OFF
    elif strategy == "ratio":
        return TraceIdRatioBased(rate)
    elif strategy == "adaptive":
        return AdaptiveSampler(
            default_rate=rate,
            error_rate=sampling_config.get("error_rate", 1.0),
            slow_threshold_ms=sampling_config.get("slow_threshold_ms", 1000),
        )
    elif strategy == "tail_based":
        return TailBasedSampler(rate)
    else:
        # Default: parent-based with ratio
        return ParentBased(root=TraceIdRatioBased(rate))
