"""
Unit tests for TripId value object.

TripId is the unique identifier for a Trip. These tests verify
that IDs can be created, compared, and serialised correctly.
"""
import pytest

from src.trips.domain.value_objects.trip_id import TripId


class TestTripId:

    def test_generate_creates_a_non_empty_id(self):
        trip_id = TripId.generate()
        assert trip_id.value
        assert len(trip_id.value) > 0

    def test_two_generated_ids_are_unique(self):
        id_a = TripId.generate()
        id_b = TripId.generate()
        assert id_a != id_b

    def test_from_string_preserves_value(self):
        raw = "abc-123"
        trip_id = TripId.from_string(raw)
        assert trip_id.value == raw

    def test_str_returns_raw_value(self):
        raw = "abc-123"
        trip_id = TripId.from_string(raw)
        assert str(trip_id) == raw

    def test_two_ids_with_same_value_are_equal(self):
        raw = "same-id"
        assert TripId.from_string(raw) == TripId.from_string(raw)

    def test_trip_id_is_immutable(self):
        trip_id = TripId.generate()
        with pytest.raises(Exception):
            trip_id.value = "new-value"
