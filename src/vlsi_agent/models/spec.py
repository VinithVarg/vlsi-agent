"""Strict internal models for FIFO specifications."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import re
from typing import Any, ClassVar


_IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class ValidationError(ValueError):
    """Raised when a FIFO spec is invalid."""


@dataclass(frozen=True)
class StrictModel:
    """Base model that rejects unknown keys and validates field values."""

    _required_fields: ClassVar[tuple[str, ...]] = ()

    @classmethod
    def _model_fields(cls) -> tuple[str, ...]:
        return tuple(field.name for field in fields(cls))

    @classmethod
    def _validate_mapping(cls, data: Any) -> dict[str, Any]:
        if not isinstance(data, dict):
            raise ValidationError(f"{cls.__name__} must be a mapping")

        expected = set(cls._model_fields())
        provided = set(data)
        unknown = sorted(provided - expected)
        if unknown:
            raise ValidationError(f"{cls.__name__} got unknown fields: {', '.join(unknown)}")

        missing = sorted(name for name in cls._required_fields or cls._model_fields() if name not in data)
        if missing:
            raise ValidationError(f"{cls.__name__} missing required fields: {', '.join(missing)}")

        return data

    @classmethod
    def model_validate(cls, data: Any) -> StrictModel:
        """Create and validate an instance from a raw mapping."""
        normalized = cls._validate_mapping(data)
        return cls(**normalized)

    def model_dump(self) -> dict[str, Any]:
        """Return a plain nested dictionary representation."""
        return asdict(self)


def _validate_identifier(field_name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")
    if not _IDENTIFIER_RE.fullmatch(value):
        raise ValidationError(f"{field_name} must be a valid identifier")
    return value


def _validate_positive_int(field_name: str, value: Any) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive integer")
    return value


@dataclass(frozen=True)
class DesignSpec(StrictModel):
    """Top-level design identity."""

    family: str
    module_name: str

    def __post_init__(self) -> None:
        if self.family != "synchronous_fifo":
            raise ValidationError("design.family must be 'synchronous_fifo'")
        object.__setattr__(self, "module_name", _validate_identifier("design.module_name", self.module_name))


@dataclass(frozen=True)
class ParametersSpec(StrictModel):
    """FIFO sizing parameters."""

    data_width: int
    depth: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "data_width", _validate_positive_int("parameters.data_width", self.data_width))
        depth = _validate_positive_int("parameters.depth", self.depth)
        if depth & (depth - 1):
            raise ValidationError("parameters.depth must be a power of two")
        object.__setattr__(self, "depth", depth)


@dataclass(frozen=True)
class PortsSpec(StrictModel):
    """Explicit FIFO port names."""

    clk: str
    rst_n: str
    wr_en: str
    rd_en: str
    wdata: str
    rdata: str
    full: str
    empty: str

    def __post_init__(self) -> None:
        for field_name in self._model_fields():
            value = getattr(self, field_name)
            object.__setattr__(self, field_name, _validate_identifier(f"ports.{field_name}", value))


@dataclass(frozen=True)
class TbSpec(StrictModel):
    """Deterministic testbench options."""

    module_name: str
    write_count: int = 4

    def __post_init__(self) -> None:
        object.__setattr__(self, "module_name", _validate_identifier("tb.module_name", self.module_name))
        object.__setattr__(self, "write_count", _validate_positive_int("tb.write_count", self.write_count))


@dataclass(frozen=True)
class FifoSpec(StrictModel):
    """Full validated FIFO specification."""

    design: DesignSpec
    parameters: ParametersSpec
    ports: PortsSpec
    tb: TbSpec

    @classmethod
    def model_validate(cls, data: Any) -> FifoSpec:
        """Create and validate a full FIFO spec from raw input data."""
        normalized = cls._validate_mapping(data)
        return cls(
            design=DesignSpec.model_validate(normalized["design"]),
            parameters=ParametersSpec.model_validate(normalized["parameters"]),
            ports=PortsSpec.model_validate(normalized["ports"]),
            tb=TbSpec.model_validate(normalized["tb"]),
        )
