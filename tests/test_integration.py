"""Here we dump all the t.py scripts quick tests as way to check 'concrete' use cases of the library."""

import polars as pl

import pql

from ._utils import assert_lf_eq_pl


# TODO: We need to implement sort and drop nulls at the expression level to be able to compare them.
def tst_funcs() -> None:
    pql_lf = pql.meta.functions()
    pl_lf = pql_lf.collect()

    unwanted = (
        "database_name",
        "database_oid",
        "schema_name",
        "comment",
        "stability",
        "tags",
        "function_oid",
        "has_side_effects",
        "macro_definition",
        "internal",
    )

    assert_lf_eq_pl(
        pql_lf.drop(unwanted)
        .filter(pql.col("function_name").str.contains(pql.lit("xor")))
        .group_by("function_name")
        .agg(pql.all(exclude="function_name").unique())
        .sort("function_name"),
        pl_lf.lazy()
        .drop(unwanted)
        .filter(pl.col("function_name").str.contains(pl.lit("xor")))
        .group_by("function_name")
        .agg(pl.all().exclude("function_name").unique().sort().drop_nulls())
        .sort("function_name"),
    )
