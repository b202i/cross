# Regression Testing Strategy for Cross

## Overview
Cross is a complex CLI application with 20+ commands, multiple AI integrations, file-based workflows, and stateful operations. This document outlines a practical, maintainable regression testing strategy.

---

## Running Tests

```bash
cd ~/github/cross
pytest                            # 412 fast unit tests  ~2s
pytest --slow                     # 412 unit + 28 CLI smoke tests  ~10s
pytest -m slow                    # 28 CLI smoke tests only  ~7s
pytest tests/test_st_plot.py -v   # run one file, verbose
pytest tests/test_st_plot.py::TestDataFramePipeline::test_guarded_drop_removes_summary_when_present -v  # single test
```

---

## Current State
- **Test infrastructure exists** — `tests/` directory, `pytest.ini`, fixtures in `tests/fixtures/`
- **78 tests passing** across `test_container_loading.py`, `test_mmd_process_report.py`, `test_st_plot.py`, `test_st_speed.py`
- **High complexity**: 20+ CLI commands, 5 AI providers, parallel execution, file I/O
- **Existing validation**: pytest unit tests; CLI commands still require manual testing

---

## Recommended Testing Strategy

### Level 1: Unit Tests (Foundation) ⭐ START HERE
Test individual functions in isolation without AI calls or file I/O.

**Priority modules to test first:**
1. `mmd_util.py` — Utility functions (data extraction, parsing, formatting)
2. `ai_handler.py` — AI selection, model mapping (mock the actual API calls)
3. `mmd_data_analysis.py` — Data aggregation, statistics
4. `discourse.py` — Config parsing, validation

**Setup:**
```bash
pip install pytest pytest-cov pytest-mock
```

**Example test file structure:**
```
tests/
├── __init__.py
├── test_mmd_util.py
├── test_ai_handler.py
├── test_data_analysis.py
├── test_discourse.py
└── fixtures/
    ├── sample_container.json
    └── sample_prompt.txt
```

**Example test (`tests/test_mmd_util.py`):**
```python
import pytest
from mmd_util import get_story_score, extract_title

def test_get_story_score_valid():
    story = {
        "fact_check": [
            {"verdict": {"True": 5, "Partially_true": 2, "False": 1}}
        ]
    }
    assert get_story_score(story, 0) == pytest.approx(0.5, rel=0.1)

def test_extract_title_from_markdown():
    text = "# My Title\n\nBody content..."
    assert extract_title(text) == "My Title"

def test_extract_title_no_heading():
    text = "Just some text without a heading"
    assert extract_title(text) == ""
```

---

### Level 2: Integration Tests (CLI Commands)
Test commands end-to-end with **mocked AI responses** and **fixture files**.

**Key insight:** Don't call real AI APIs in tests — use recorded responses.

**Setup:**
```bash
pip install pytest-subprocess responses
```

**Example test (`tests/test_st_gen.py`):**
```python
import json
import pytest
from pathlib import Path
from unittest.mock import patch

def test_st_gen_creates_valid_json(tmp_path, mock_ai_response):
    """Test st-gen with a mocked AI response"""
    prompt_file = tmp_path / "test.prompt"
    prompt_file.write_text("Write about bicycles")
    
    output_file = tmp_path / "test.json"
    
    with patch('ai_handler.process_prompt', return_value=mock_ai_response):
        # Run the command
        from st_gen import main
        import sys
        sys.argv = ['st-gen', '--ai', 'xai', str(prompt_file)]
        main()
    
    # Verify output
    assert output_file.exists()
    container = json.loads(output_file.read_text())
    assert "data" in container
    assert "story" in container
    assert len(container["story"]) == 1

@pytest.fixture
def mock_ai_response():
    """Fixture providing a canned AI response"""
    return {
        "text": "# Bicycles\n\nBicycles are vehicles...",
        "model": "grok-4-1-fast-reasoning",
        "timestamp": "2026-03-19T10:00:00Z"
    }
```

---

### Level 3: Snapshot Testing (Output Validation)
For commands that produce formatted output (tables, reports), use snapshot tests to detect unintended changes.

**Setup:**
```bash
pip install pytest-snapshot
```

**Example test (`tests/test_st_ls.py`):**
```python
def test_st_ls_table_format(snapshot, fixture_container):
    """Ensure st-ls table output format doesn't regress"""
    from st_ls import format_story_table
    
    output = format_story_table(fixture_container)
    snapshot.assert_match(output, 'st_ls_table.txt')
```

**How it works:**
- First run: saves output to `tests/snapshots/st_ls_table.txt`
- Subsequent runs: compares new output to saved snapshot
- If different: test fails, showing diff
- If intentional: run `pytest --snapshot-update` to accept new output

---

### Level 4: End-to-End Workflow Tests
Test complete workflows with fixture files and mocked AI calls.

**Example test (`tests/test_workflow_basic.py`):**
```python
def test_full_generation_workflow(tmp_path, mock_all_ais):
    """Test: new prompt → bang → fact-check → merge"""
    
    # 1. Create prompt
    prompt = tmp_path / "test.prompt"
    prompt.write_text("Write about the Cruzbike S40")
    
    # 2. Run st-bang (mocked AI responses)
    with patch_ai_responses(mock_all_ais):
        run_command(['st-bang', str(prompt)])
    
    # 3. Verify container created
    container_file = tmp_path / "test.json"
    assert container_file.exists()
    container = json.loads(container_file.read_text())
    assert len(container["story"]) == 5  # All 5 AI
    
    # 4. Run st-cross (mocked fact-checks)
    with patch_ai_responses(mock_fact_checks):
        run_command(['st-cross', str(container_file)])
    
    # 5. Verify fact-checks added
    container = json.loads(container_file.read_text())
    for story in container["story"]:
        assert len(story.get("fact_check", [])) == 5
    
    # 6. Run st-merge
    with patch_ai_responses(mock_merge):
        run_command(['st-merge', str(container_file)])
    
    # 7. Verify merged story created
    container = json.loads(container_file.read_text())
    assert len(container["story"]) == 6  # 5 original + 1 merged
```

---

### Level 5: Regression Test Suite (Golden Files)
Maintain a set of "known good" containers and test critical commands against them.

**Structure:**
```
tests/
└── golden/
    ├── cruzbike_s40_gen1.json      # Known good container
    ├── pizza_dough.json             # Simple test case
    └── expected_outputs/
        ├── cruzbike_analyze.txt     # Expected st-analyze output
        └── cruzbike_read.txt        # Expected st-read output
```

**Example test (`tests/test_golden.py`):**
```python
def test_analyze_output_matches_golden():
    """Ensure st-analyze produces consistent output for known input"""
    golden_file = Path("tests/golden/cruzbike_s40_gen1.json")
    expected_output = Path("tests/golden/expected_outputs/cruzbike_analyze.txt").read_text()
    
    result = run_command(['st-analyze', '--ai', 'xai', str(golden_file)], capture=True)
    
    # Allow minor floating-point differences
    assert results_match_within_tolerance(result.stdout, expected_output, tolerance=0.1)
```

---

## Mock Strategy for AI Providers

### Option 1: Response Recording (Recommended)
Record real API responses once, replay them in tests.

**Setup:**
```bash
pip install vcrpy
```

**Usage:**
```python
import vcr

@vcr.use_cassette('tests/cassettes/xai_bicycles.yaml')
def test_xai_generation():
    """First run: records response. Subsequent runs: replays recording."""
    response = call_xai_api("Write about bicycles")
    assert "bicycle" in response.lower()
```

**Benefits:**
- Tests use real API response structure
- No manual mocking required
- Cassettes are human-readable YAML

**Workflow:**
1. Run tests once with `--record-mode=once` (creates cassettes)
2. Commit cassettes to git
3. CI/CD runs tests using cassettes (no API keys needed)
4. Re-record when API changes

### Option 2: Manual Mocks
For unit tests where you need precise control.

```python
from unittest.mock import patch, MagicMock

@patch('ai_openai.get_openai_response')
def test_openai_error_handling(mock_get):
    mock_get.side_effect = Exception("Rate limit exceeded")
    
    with pytest.raises(Exception, match="Rate limit"):
        generate_story("xai", "test prompt")
```

---

## Test Organization

### Recommended pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --ignore=.venv
    --ignore=story
    --ignore=tmp
```

### Coverage Goals
- **Phase 1 (MVP)**: 40% coverage — all utility functions, core parsers
- **Phase 2 (Stable)**: 60% coverage — add CLI command tests
- **Phase 3 (Production)**: 75% coverage — add workflow tests

---

## Continuous Integration

### GitHub Actions Workflow (`.github/workflows/test.yml`)
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11"]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-mock vcrpy
    
    - name: Run tests
      run: pytest --cov --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
```

---

## Quick Start: First Test in 10 Minutes

### 1. Install pytest
```bash
pip install pytest pytest-mock
pip freeze > requirements-dev.txt  # Save dev dependencies
```

### 2. Create test directory
```bash
mkdir -p tests/fixtures
touch tests/__init__.py
```

### 3. Add a fixture file
```bash
# Copy an existing container as a test fixture
cp ~/github/cross-story/mmd/pizza_dough.json tests/fixtures/
```

### 4. Write your first test (`tests/test_container_loading.py`)
```python
import json
import pytest
from pathlib import Path

def test_load_container_has_required_keys():
    """Verify basic container structure"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    assert "data" in container
    assert "story" in container
    assert isinstance(container["data"], list)
    assert isinstance(container["story"], list)

def test_story_has_required_fields():
    """Verify story structure"""
    fixture = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    
    with open(fixture) as f:
        container = json.load(f)
    
    if container["story"]:
        story = container["story"][0]
        assert "make" in story
        assert "model" in story
        assert "title" in story or "markdown" in story
```

### 5. Run the test
```bash
pytest tests/test_container_loading.py -v
```

**Expected output:**
```
tests/test_container_loading.py::test_load_container_has_required_keys PASSED
tests/test_container_loading.py::test_story_has_required_fields PASSED
```

---

## Testing Best Practices

### DO ✅
- **Mock AI calls** — never call real APIs in tests
- **Use fixtures** — reuse test data across multiple tests
- **Test error paths** — missing files, malformed JSON, API errors
- **Keep tests fast** — entire suite should run in < 30 seconds
- **Test public interfaces** — focus on command-line behavior, not internal details
- **Use descriptive names** — `test_st_fix_improves_false_claims` not `test_fix`

### DON'T ❌
- **Don't test external APIs** — you don't control them
- **Don't commit API keys** — use mocks or cassettes
- **Don't test private functions** — test the public API instead
- **Don't make tests depend on each other** — each test should be independent
- **Don't test implementation details** — test behavior, not code structure

---

## Priority Testing Roadmap

### Week 1: Foundation
- [ ] Install pytest, create test directory structure
- [ ] Write 10 unit tests for `mmd_util.py`
- [ ] Set up fixtures directory with 3 sample containers
- [ ] Configure pytest.ini

### Week 2: Core Commands
- [ ] Mock AI responses using vcr.py
- [ ] Write integration tests for `st-gen`, `st-bang`, `st-ls`
- [ ] Add snapshot tests for table outputs

### Week 3: Complex Workflows
- [ ] Test `st-fact` with mocked AI calls
- [ ] Test `st-merge` with quality mode
- [ ] Test `st-fix` iterate mode

### Week 4: CI/CD
- [ ] Set up GitHub Actions workflow
- [ ] Add coverage reporting (aim for 40%)
- [ ] Document testing process in README

---

## FAQ

**Q: Do I need to test every command?**  
A: No. Start with the most critical/complex ones: `st-bang`, `st-fact`, `st-cross`, `st-merge`, `st-fix`.

**Q: How do I test commands that require user input?**  
A: Mock `input()` or use pytest's `monkeypatch` fixture to inject responses.

**Q: Should I test the interactive `st` menu?**  
A: No. Menu logic is simple dispatch — test the underlying commands instead.

**Q: How do I test parallel execution (st-bang, st-cross)?**  
A: Mock the subprocess calls and verify the command strings are correct.

**Q: What about testing Discourse posting?**  
A: Mock the `requests` library calls. Use `responses` library to fake HTTP responses.

**Q: How do I test timing data collection?**  
A: Use `freezegun` to control time, or mock `time.time()`.

**Q: Should I test with the API cache enabled?**  
A: Tests should run with `--no-cache` to ensure reproducibility.

---

## Tools Summary

| Tool | Purpose | Install |
|------|---------|---------|
| pytest | Test framework | `pip install pytest` |
| pytest-cov | Coverage reporting | `pip install pytest-cov` |
| pytest-mock | Enhanced mocking | `pip install pytest-mock` |
| vcrpy | Record/replay API calls | `pip install vcrpy` |
| responses | Mock HTTP requests | `pip install responses` |
| pytest-snapshot | Snapshot testing | `pip install pytest-snapshot` |
| freezegun | Time mocking | `pip install freezegun` |
| pytest-subprocess | Mock subprocesses | `pip install pytest-subprocess` |

---

## Example: Complete Test File

**`tests/test_st_read.py`:**
```python
import pytest
import json
from pathlib import Path
from unittest.mock import patch
from io import StringIO

def test_st_read_displays_scores(fixture_container, capsys):
    """Test st-read shows readability metrics"""
    from st_read import display_scores
    
    stories = fixture_container["story"]
    display_scores(stories)
    
    captured = capsys.readouterr()
    assert "Dale" in captured.out
    assert "Gunning" in captured.out
    assert "Smog" in captured.out

def test_st_read_rounds_to_one_decimal():
    """Test that scores are rounded to 1 decimal place"""
    from st_read import format_score
    
    assert format_score(13.935) == "13.9"
    assert format_score(25.5251) == "25.5"
    assert format_score(0.792065) == "0.8"

@pytest.fixture
def fixture_container():
    """Load a fixture container"""
    path = Path(__file__).parent / "fixtures" / "pizza_dough.json"
    with open(path) as f:
        return json.load(f)
```

---

## Next Steps

1. **Start small**: Implement the "First Test in 10 Minutes" section above
2. **Expand coverage**: Add one test file per week
3. **Run tests regularly**: `pytest` before every commit
4. **Integrate with CI**: Set up GitHub Actions when you have 20+ tests
5. **Document patterns**: Add examples to this file as you discover best practices

---

## Related Documentation
- [README_install.md](README_install.md) — Installation guide
- [README_opensource.md](README_opensource.md) — Project overview
- [PHASE1_IMPLEMENTATION.md](PHASE1_IMPLEMENTATION.md) — Timing data capture implementation

---

**Last updated:** March 23, 2026  
**Status:** Active — 78 tests passing; expanding coverage

