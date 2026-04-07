import polars as pl
import pytest

import pql

from ._utils import assert_eq


def test_name_keep_after_alias() -> None:
    assert_eq(
        pql.col("x").alias("renamed").name.keep(),
        pl.col("x").alias("renamed").name.keep(),
    )


def test_name_map() -> None:
    assert_eq(
        pql.col("x").name.map(lambda name: f"mapped_{name}"),
        pl.col("x").name.map(lambda name: f"mapped_{name}"),
    )


def test_name_prefix_suffix() -> None:
    assert_eq(
        pql.col("x").name.prefix("pre_").name.suffix("_suf"),
        pl.col("x").name.prefix("pre_").name.suffix("_suf"),
    )


def test_name_case_transform() -> None:
    assert_eq(
        pql.col("x").name.to_uppercase().name.to_lowercase(),
        pl.col("x").name.to_uppercase().name.to_lowercase(),
    )


case_skip = pytest.mark.skip(
    reason="This test is currently failing due to an issue with column name traduction to polars dataframe/pandas"
)


@case_skip
def test_name_to_uppercase_all() -> None:
    assert_eq(
        pql.all().name.to_uppercase(),
        pl.all().name.to_uppercase(),
    )


@pytest.mark.parametrize("literal", [True, False])
def test_name_replace(literal: bool) -> None:
    assert_eq(
        pql.col("x").name.replace("x", "y", literal=literal),
        pl.col("x").name.replace("x", "y", literal=literal),
    )
    assert_eq(
        pql.col("s").name.replace("s", "t", literal=literal),
        pl.col("s").name.replace("s", "t", literal=literal),
    )
    assert_eq(
        pql.col("salary").name.replace("salary", "income", literal=literal),
        pl.col("salary").name.replace("salary", "income", literal=literal),
    )

    assert_eq(
        pql.col("salary").name.replace("a", "b", literal=literal),
        pl.col("salary").name.replace("a", "b", literal=literal),
    )


@case_skip
def test_name_replace_case_sensitivity(literal: bool) -> None:
    assert_eq(
        pql.col("salary").name.replace("l", "L", literal=literal),
        pl.col("salary").name.replace("l", "L", literal=literal),
    )
    assert_eq(
        pql.col("salary").name.replace("sal", "SAL", literal=literal),
        pl.col("salary").name.replace("sal", "SAL", literal=literal),
    )
