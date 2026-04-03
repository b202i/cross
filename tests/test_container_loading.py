"""
Basic tests for container loading and structure validation.

These tests verify the fundamental JSON container format used by Cross.
They serve as a starting point for regression testing.
"""
import json
import pytest
from pathlib import Path


def test_load_container_has_required_keys():
    """Verify basic container structure has 'data' and 'story' keys"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    assert "data" in container, "Container must have 'data' key"
    assert "story" in container, "Container must have 'story' key"
    assert isinstance(container["data"], list), "'data' must be a list"
    assert isinstance(container["story"], list), "'story' must be a list"


def test_story_has_required_fields():
    """Verify story objects have minimum required fields"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    if container["story"]:
        story = container["story"][0]
        assert "make" in story, "Story must have 'make' field (AI provider)"
        assert "model" in story, "Story must have 'model' field"
        # At least one content field must exist
        has_content = any(key in story for key in ["title", "markdown", "text", "spoken"])
        assert has_content, "Story must have at least one content field"


def test_data_entries_have_required_fields():
    """Verify data entries have required fields"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    if container["data"]:
        data_entry = container["data"][0]
        assert "make" in data_entry, "Data entry must have 'make' field"
        assert "model" in data_entry, "Data entry must have 'model' field"
        assert "md5_hash" in data_entry, "Data entry must have 'md5_hash' field"
        # Either gen_response or raw response should exist
        has_response = "gen_response" in data_entry or "response" in data_entry
        assert has_response, "Data entry must have response data"


def test_fact_check_structure():
    """Verify fact-check data structure when present"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    for story in container["story"]:
        if "fact_check" in story:
            fact_checks = story["fact_check"]
            assert isinstance(fact_checks, list), "fact_check must be a list"
            
            if fact_checks:
                fc = fact_checks[0]
                assert "make" in fc, "Fact-check must have 'make' (checker AI)"
                assert "verdict" in fc, "Fact-check must have 'verdict'"


def test_container_json_is_valid():
    """Ensure container can be serialized back to JSON"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    # Should be able to serialize without errors
    json_str = json.dumps(container, ensure_ascii=False, indent=4)
    assert len(json_str) > 0
    
    # Should be able to deserialize back
    reloaded = json.loads(json_str)
    assert reloaded == container

