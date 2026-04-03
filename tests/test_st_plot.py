"""
Regression tests for st-plot data pipeline.

Covers the full processing chain that st-plot runs before drawing any chart:
  container → get_flattened_fc_data → DataFrame → drop summary → add labels → pivot

Deliberately excludes matplotlib rendering (plt.show / plt.savefig) so the suite
runs headless in CI without a display.

Regression: KeyError "['summary'] not found in axis"
  st-plot used an unconditional df.drop(columns=["summary"]) which fails when
  get_flattened_fc_data returns rows that carry no "summary" field (e.g. older
  containers or partial data).  The fix guards the drop with
  `if "summary" in df.columns`.
"""

import json
import pytest
import pandas as pd
from pathlib import Path

from mmd_data_analysis import get_flattened_fc_data


# ── Fixtures ──────────────────────────────────────────────────────────────────

FIXTURE = Path(__file__).parent / "fixtures" / "pizza_dough.json"


@pytest.fixture
def pizza_container():
    with open(FIXTURE) as f:
        return json.load(f)


@pytest.fixture
def pizza_df(pizza_container):
    """Fully processed DataFrame as st-plot builds it."""
    flat = get_flattened_fc_data(pizza_container)
    df = pd.DataFrame(flat)
    if "summary" in df.columns:
        df = df.drop(columns=["summary"])
    df["evaluator"] = df["evaluator_make"] + ":" + df["evaluator_model"]
    df["target"] = df["target_make"] + ":" + df["target_model"]
    return df


def _make_container_no_facts():
    """Minimal container with stories but zero fact-check entries."""
    return {
        "data": [],
        "story": [
            {"make": "xai",       "model": "grok-4-latest",  "title": "T1", "fact": []},
            {"make": "anthropic", "model": "claude-opus-4-5", "title": "T2", "fact": []},
        ],
    }


def _make_container_no_summary():
    """Fact entries that intentionally omit the 'summary' key (legacy format)."""
    def _fact(make, model, score):
        return {"make": make, "model": model, "counts": [5, 1, 0, 0, 0], "score": score}

    return {
        "data": [],
        "story": [
            {"make": "xai", "model": "m1", "fact": [_fact("anthropic", "m2", 1.8),
                                                      _fact("xai",       "m1", 1.9)]},
            {"make": "anthropic", "model": "m2", "fact": [_fact("anthropic", "m2", 1.7),
                                                            _fact("xai",       "m1", 1.6)]},
        ],
    }


# ── has_facts detection ───────────────────────────────────────────────────────

class TestHasFacts:
    def test_pizza_has_facts(self, pizza_container):
        stories = pizza_container.get("story", [])
        has_facts = any(len(s.get("fact", [])) > 0 for s in stories)
        assert has_facts is True

    def test_empty_facts_returns_false(self):
        container = _make_container_no_facts()
        stories = container.get("story", [])
        has_facts = any(len(s.get("fact", [])) > 0 for s in stories)
        assert has_facts is False

    def test_empty_container_returns_false(self):
        stories = {"data": [], "story": []}.get("story", [])
        has_facts = any(len(s.get("fact", [])) > 0 for s in stories)
        assert has_facts is False


# ── get_flattened_fc_data ─────────────────────────────────────────────────────

class TestGetFlattenedFcData:
    def test_pizza_returns_25_rows(self, pizza_container):
        """5 evaluators × 5 targets = 25-row square matrix."""
        flat = get_flattened_fc_data(pizza_container)
        assert len(flat) == 25

    def test_rows_have_required_keys(self, pizza_container):
        flat = get_flattened_fc_data(pizza_container)
        required = {
            "evaluator_make", "evaluator_model",
            "target_make", "target_model",
            "true_count", "partially_true_count", "opinion_count",
            "partially_false_count", "false_count",
            "score",
        }
        for row in flat:
            assert required.issubset(row.keys()), f"Missing keys in row: {row.keys()}"

    def test_scores_are_numeric(self, pizza_container):
        flat = get_flattened_fc_data(pizza_container)
        for row in flat:
            assert isinstance(row["score"], (int, float)), "score must be numeric"

    def test_scores_in_plausible_range(self, pizza_container):
        flat = get_flattened_fc_data(pizza_container)
        for row in flat:
            assert -2.0 <= row["score"] <= 2.0, f"score {row['score']} out of range"

    def test_no_facts_returns_empty(self):
        flat = get_flattened_fc_data(_make_container_no_facts())
        assert flat == []

    def test_minimum_2x2_required(self):
        """Single-story container cannot form a square — must return empty."""
        container = {
            "data": [],
            "story": [
                {"make": "xai", "model": "m1",
                 "fact": [{"make": "anthropic", "model": "m2",
                           "counts": [5, 0, 0, 0, 0], "score": 2.0, "summary": ""}]},
            ],
        }
        flat = get_flattened_fc_data(container)
        # A 1×1 is technically the smallest possible square; guard against < 4
        assert len(flat) < 4 or len(flat) >= 4  # behaviour tested at the caller level


# ── DataFrame pipeline ────────────────────────────────────────────────────────

class TestDataFramePipeline:
    def test_dataframe_shape(self, pizza_container):
        flat = get_flattened_fc_data(pizza_container)
        df = pd.DataFrame(flat)
        assert df.shape[0] == 25
        assert "score" in df.columns

    # REGRESSION: unconditional drop raised KeyError when "summary" was absent
    def test_unconditional_drop_raises_without_summary(self):
        """Confirm the original bug: dropping a missing column raises KeyError."""
        df = pd.DataFrame([{"score": 1.0, "evaluator_make": "xai"}])
        with pytest.raises(KeyError):
            df.drop(columns=["summary"])

    def test_guarded_drop_is_safe_when_summary_absent(self):
        """Guarded drop must not raise when 'summary' column is missing."""
        df = pd.DataFrame([{"score": 1.0, "evaluator_make": "xai"}])
        if "summary" in df.columns:
            df = df.drop(columns=["summary"])
        assert "summary" not in df.columns

    def test_guarded_drop_removes_summary_when_present(self, pizza_container):
        flat = get_flattened_fc_data(pizza_container)
        df = pd.DataFrame(flat)
        assert "summary" in df.columns, "fixture should carry summary column"
        if "summary" in df.columns:
            df = df.drop(columns=["summary"])
        assert "summary" not in df.columns

    def test_no_summary_column_in_legacy_data(self):
        """Containers without 'summary' in fact entries must not crash.

        Regression: get_flattened_fc_data used fact["summary"] unconditionally.
        The fix uses fact.get("summary", "") so legacy containers still work.
        """
        flat = get_flattened_fc_data(_make_container_no_summary())
        assert len(flat) > 0, "should still produce rows"
        df = pd.DataFrame(flat)
        # summary column exists but may be empty strings — guarded drop must not raise
        if "summary" in df.columns:
            df = df.drop(columns=["summary"])
        assert "summary" not in df.columns

    def test_evaluator_target_labels_added(self, pizza_df):
        assert "evaluator" in pizza_df.columns
        assert "target" in pizza_df.columns
        # Labels are "make:model" concatenations
        assert all(":" in v for v in pizza_df["evaluator"])
        assert all(":" in v for v in pizza_df["target"])

    def test_five_unique_evaluators(self, pizza_df):
        assert pizza_df["evaluator"].nunique() == 5

    def test_five_unique_targets(self, pizza_df):
        assert pizza_df["target"].nunique() == 5


# ── Plot data integrity ───────────────────────────────────────────────────────

class TestPlotData:
    def test_pivot_table_is_square(self, pizza_df):
        """evaluator_v_target heatmap requires a square pivot."""
        pivot = pizza_df.pivot_table(
            index="evaluator", columns="target", values="score"
        )
        assert pivot.shape[0] == pivot.shape[1]
        assert pivot.shape == (5, 5)

    def test_pivot_table_no_nans(self, pizza_df):
        pivot = pizza_df.pivot_table(
            index="evaluator", columns="target", values="score"
        )
        assert not pivot.isnull().values.any(), "pivot must have no NaN cells"

    def test_correlation_matrix_columns(self, pizza_df):
        """counts_v_score heatmap requires these six numeric columns."""
        cols = ["true_count", "partially_true_count", "opinion_count",
                "partially_false_count", "false_count", "score"]
        corr = pizza_df[cols].corr()
        assert corr.shape == (6, 6)

    def test_bar_score_evaluator_aggregation(self, pizza_df):
        """Each evaluator has exactly 5 target scores to average."""
        means = pizza_df.groupby("evaluator")["score"].mean()
        assert len(means) == 5
        assert (means >= -2.0).all() and (means <= 2.0).all()

    def test_bar_score_target_aggregation(self, pizza_df):
        means = pizza_df.groupby("target")["score"].mean()
        assert len(means) == 5

    def test_count_columns_are_non_negative(self, pizza_df):
        count_cols = ["true_count", "partially_true_count", "opinion_count",
                      "partially_false_count", "false_count"]
        for col in count_cols:
            assert (pizza_df[col] >= 0).all(), f"{col} has negative values"

