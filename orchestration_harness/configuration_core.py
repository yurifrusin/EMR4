"""Pure configuration boundary for controller adapters.

``validate_configuration`` consumes an exact set of document bytes, independently
expected SHA-256 values, fixed schema declarations, and typed reference edges.
The caller authenticates those expectations and the adapter source. Documents
cannot supply their own authority. Output contains immutable canonical bytes and
identities; it is a validation result, never an execution or publication token.
There is no filesystem, environment, repository discovery, or effect interface.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

import yaml


class ConfigurationError(ValueError):
    def __init__(self, reason_code: str):
        super().__init__(reason_code)
        self.reason_code = reason_code


def _need(condition: bool, reason: str) -> None:
    if not condition:
        raise ConfigurationError(reason)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        _need(type(key) is str and key not in result, "configuration_duplicate_or_invalid_key")
        result[key] = value
    return result


def canonical(value: object) -> bytes:
    seen = set()
    remaining = 50000

    def visit(item, depth):
        nonlocal remaining
        remaining -= 1
        _need(remaining >= 0 and depth <= 64, "configuration_structure_bound")
        if type(item) in (dict, list):
            _need(id(item) not in seen, "configuration_alias_or_cycle")
            seen.add(id(item))
            if type(item) is dict:
                _need(all(type(k) is str for k in item), "configuration_duplicate_or_invalid_key")
                children = item.values()
            else:
                children = item
            for child in children:
                visit(child, depth + 1)
        else:
            _need(type(item) in (str, int, float, bool, type(None)), "configuration_value_type")
            _need(type(item) is not float or math.isfinite(item), "configuration_nonfinite_number")

    visit(value, 0)
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                          allow_nan=False).encode("utf-8")
    except (ValueError, UnicodeError) as error:
        raise ConfigurationError("configuration_encoding") from error


class _Yaml(yaml.SafeLoader):
    def compose_node(self, parent, index):
        _need(not self.check_event(yaml.AliasEvent), "configuration_alias_or_cycle")
        event = self.peek_event()
        _need(getattr(event, "anchor", None) is None, "configuration_alias_or_cycle")
        return super().compose_node(parent, index)


def _mapping(loader, node, deep=False):
    return _pairs((loader.construct_object(key, deep=deep), loader.construct_object(value, deep=deep))
                  for key, value in node.value)


_Yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def _reject_constant(_value):
    raise ConfigurationError("configuration_nonfinite_number")


def decode(raw: bytes, encoding: str) -> dict:
    _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "configuration_document_size")
    _need(not raw.startswith(b"\xef\xbb\xbf"), "configuration_encoding")
    try:
        text = raw.decode("utf-8", errors="strict")
        if encoding == "json":
            value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_reject_constant)
        elif encoding == "yaml":
            value = yaml.load(text, Loader=_Yaml)
        else:
            raise ConfigurationError("configuration_encoding")
        _need(type(value) is dict, "configuration_object_required")
        canonical(value)
        return value
    except (UnicodeError, yaml.YAMLError, json.JSONDecodeError, RecursionError) as error:
        raise ConfigurationError("configuration_decode_invalid") from error


def validate_shape(value: object, schema: tuple, depth: int = 0) -> None:
    """Validate a fixed declaration, including every nested key and value type.

    Declarations are immutable tuples: object(properties, optional names),
    array(item alternatives), literal(value), string(allow empty), integer,
    number, boolean, or null. The adapter also checks domain-specific semantics.
    """
    _need(depth <= 64 and type(schema) is tuple and bool(schema), "configuration_schema_declaration")
    kind = schema[0]
    reason = "configuration_schema_invalid"
    if kind == "object":
        _need(len(schema) == 3 and type(value) is dict, reason)
        properties, optional = dict(schema[1]), frozenset(schema[2])
        _need(len(properties) == len(schema[1]) and optional <= properties.keys(),
              "configuration_schema_declaration")
        _need(set(value) <= properties.keys() and properties.keys() - optional <= set(value), reason)
        for key, item in value.items():
            validate_shape(item, properties[key], depth + 1)
    elif kind == "array":
        _need(len(schema) == 2 and type(value) is list and 1 <= len(schema[1]) <= 32, reason)
        for item in value:
            for alternative in schema[1]:
                try:
                    validate_shape(item, alternative, depth + 1)
                    break
                except ConfigurationError as error:
                    if error.reason_code != reason:
                        raise
            else:
                raise ConfigurationError(reason)
    elif kind == "literal":
        _need(len(schema) == 2 and type(value) is type(schema[1]) and value == schema[1], reason)
    elif kind == "string":
        _need(len(schema) == 2 and type(value) is str and (schema[1] is True or bool(value)), reason)
    elif kind == "integer":
        _need(len(schema) == 1 and type(value) is int and 0 <= value <= 2**63 - 1, reason)
    elif kind == "number":
        _need(len(schema) == 1 and type(value) in (int, float) and value >= 0
              and (value <= 2**63 - 1 if type(value) is int else math.isfinite(value)), reason)
    elif kind == "boolean":
        _need(len(schema) == 1 and type(value) is bool, reason)
    elif kind == "null":
        _need(len(schema) == 1 and value is None, reason)
    else:
        raise ConfigurationError("configuration_schema_declaration")


@dataclass(frozen=True, slots=True)
class Reference:
    source: str
    fields: tuple[str, ...]
    target: str


@dataclass(frozen=True, slots=True)
class ValidatedConfiguration:
    documents: tuple[tuple[str, bytes], ...]
    source_sha256: tuple[tuple[str, str], ...]
    references: tuple[Reference, ...]
    canonical_sha256: str


def _name(name: object) -> bool:
    return type(name) is str and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]{0,127}", name) is not None


def validate_configuration(*, documents: dict[str, bytes], expected_sha256: dict[str, str],
                           schemas: dict[str, tuple[str, tuple]], references: tuple[Reference, ...],
                           roots: tuple[str, ...]) -> ValidatedConfiguration:
    """Validate a caller-authenticated, closed document graph without observing it."""
    _need(type(documents) is dict and type(expected_sha256) is dict and type(schemas) is dict,
          "configuration_input_mapping")
    _need(1 <= len(schemas) <= 64 and set(documents) == set(expected_sha256) == set(schemas),
          "configuration_document_set")
    _need(all(_name(name) for name in schemas), "configuration_document_name")
    _need(type(references) is tuple and len(references) <= 256 and type(roots) is tuple
          and 1 <= len(roots) == len(set(roots)) and set(roots) <= set(schemas), "configuration_reference_declaration")
    values, encoded = {}, {}
    for name in sorted(schemas):
        raw, digest = documents[name], expected_sha256[name]
        _need(type(raw) is bytes and len(raw) <= 2 * 1024 * 1024, "configuration_document_size")
        _need(type(digest) is str and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
              "configuration_expected_digest")
        _need(hashlib.sha256(raw).hexdigest() == digest, "configuration_document_changed")
        encoding, schema = schemas[name]
        value = decode(raw, encoding)
        validate_shape(value, schema)
        values[name], encoded[name] = value, canonical(value)
    edges, fields_seen = {name: set() for name in schemas}, set()
    for reference in references:
        _need(type(reference) is Reference and reference.source in schemas and reference.target in schemas
              and type(reference.fields) is tuple and bool(reference.fields)
              and all(type(field) is str for field in reference.fields), "configuration_reference_declaration")
        key = (reference.source, reference.fields)
        _need(key not in fields_seen, "configuration_reference_declaration")
        fields_seen.add(key)
        value = values[reference.source]
        for field in reference.fields:
            _need(type(value) is dict and field in value, "configuration_reference_missing")
            value = value[field]
        _need(_name(value) and value == reference.target, "configuration_reference_invalid")
        edges[reference.source].add(reference.target)
    reached, pending = set(), list(roots)
    while pending:
        name = pending.pop()
        if name not in reached:
            reached.add(name)
            pending.extend(edges[name] - reached)
    _need(reached == set(schemas), "configuration_reference_unreachable")
    identity = {name: json.loads(encoded[name]) for name in sorted(encoded)}
    return ValidatedConfiguration(tuple(sorted(encoded.items())), tuple(sorted(expected_sha256.items())),
                                  references, hashlib.sha256(canonical(identity)).hexdigest())
