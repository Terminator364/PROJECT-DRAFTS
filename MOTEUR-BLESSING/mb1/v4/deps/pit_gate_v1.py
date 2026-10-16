#!/usr/bin/env python3
"""Offline conservative chronological-gate check. NOT independent PIT certification.

Supports verification of *supplied* bytes and UTC timing constraints, while
explicitly reserving historical point-in-time authenticity for independent
archival evidence. Files bearing no capture time are not accepted.
"""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import re

HEX = re.compile(r'[0-9a-fA-F]{64}\Z')


def utc(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a string')
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as err:
        raise ValueError('invalid ISO-8601 timestamp') from err
    if d.tzinfo is None or d.utcoffset() is None:
        raise ValueError('no timezone means ambiguous PIT evidence')
    return d.astimezone(timezone.utc)


def evaluate(record: dict, raw_bytes: bytes | None = None) -> dict:
    required = ('publication_utc', 'capture_utc', 'freeze_utc', 'kickoff_utc',
                'raw_sha256', 'source_uri', 'fixture_id', 'world_id', 'subparameter_id')
    missing = [k for k in required if not record.get(k)]
    if missing:
        return {'chronology_ok': False, 'independently_authenticated': False,
                'errors': ['MISSING:' + ','.join(missing)]}
    errors=[]
    try:
        pub, cap, freeze, kick = (utc(record[k]) for k in ('publication_utc','capture_utc','freeze_utc','kickoff_utc'))
        if not pub <= cap <= freeze < kick:
            errors.append('TIME_ORDER: require publication <= capture <= freeze < kickoff')
    except ValueError as err:
        errors.append('TIMESTAMP:' + str(err))
    if not HEX.fullmatch(str(record['raw_sha256'])):
        errors.append('INVALID_SHA256')
    elif raw_bytes is None:
        errors.append('RAW_BYTES_MISSING')
    elif hashlib.sha256(raw_bytes).hexdigest() != record['raw_sha256'].lower():
        errors.append('RAW_SHA256_MISMATCH')
    if not isinstance(record['source_uri'], str) or not record['source_uri'].startswith(('https://', 'http://')):
        errors.append('SOURCE_URI_UNVERIFIED_OR_INVALID')
    return {
        'chronology_ok': not errors,
        'independently_authenticated': False, # user-supplied timestamps alone cannot establish history
        'errors': errors,
        'next_required': 'IMMUTABLE_INDEPENDENT_PREMATCH_ARCHIVE_OR_VERIFIED_SOURCE_LOG'
    }
