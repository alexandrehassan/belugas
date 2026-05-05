
# pql

Write Polars-style queries, compile them to DuckDB, and keep access to DuckDB-specific features.

`pql` is a lazy dataframe library for DuckDB. It aims to feel familiar to Polars users while staying honest about DuckDB semantics instead of hiding them behind a compatibility layer.

At a glance, `pql` gives you:

- a Polars-like `LazyFrame` and `Expr` API
- DuckDB-backed execution
- SQL inspection tools for understanding generated queries
- 200+ DuckDB-backed expression methods
- native support for DuckDB-specific features such as geometry types and functions
- direct conversion back to native Polars objects with `.collect()` and `.lazy()`

This project is still early, but it already covers a meaningful part of the Polars lazy API and exposes a large amount of DuckDB surface that Polars does not target directly.

## Why `pql`

`pql` is designed for the case where you want all of the following at once:

- DuckDB as the execution engine
- a fluent dataframe API instead of handwritten SQL
- a syntax close to Polars rather than Spark, Pandas, or Ibis
- visibility into the generated SQL when you need it
- access to DuckDB-specific functionality

In other words: `pql` is not trying to be a universal dataframe abstraction. It is trying to be a good DuckDB-native query builder for people who like Polars ergonomics.

## Quick Start

### Installation

```shell
uv add https://github.com/OutSquareCapital/pql.git
```

### Example

```python
import pql

data = {
    "city": ["Paris", "Paris", "Berlin", "Berlin"],
    "price": [100, 120, 80, 90],
    "qty": [1, 2, 3, 4],
    "is_promo": [False, True, False, True],
}
query = (
    pql
    .from_dict(data)
    .filter(pql.col("price").ge(90))
    .with_columns(revenue=pql.col("price").mul("qty"))
    .group_by("city")
    .agg(
        total_revenue=pql.col("revenue").sum(),
        avg_price=pql.col("price").mean(),
        promo_rows=pql.col("is_promo").sum(),
    )
    .sort("total_revenue", descending=True)
)
```

Output:

```shell
 ┌─────────┬───────────────┬───────────┬────────────┐
 │  city   │ total_revenue │ avg_price │ promo_rows │
 │ varchar │    int128     │  double   │   int128   │
 ├─────────┼───────────────┼───────────┼────────────┤
 │ Berlin  │           360 │      90.0 │          1 │
 │ Paris   │           340 │     110.0 │          1 │
 └─────────┴───────────────┴───────────┴────────────┘
```

You can inspect the generated SQL query directly, format it, with syntax highlighting and various available themes:

```python
import pql

query = pql.LazyFrame({"x": [1, 2, 3]}).filter(pql.col("x").gt(1))
sql = query.sql_query()

sql.show("friendly")
print("---" * 10)
sql.prettify().show()
```

![alt text](docs\sql_highlight.png)

You can also inspect the DuckDB plan:

```python
print(query.explain())
```

Output:

```shell
┌───────────────────────────┐
│         PROJECTION        │
│    ────────────────────   │
│             #1            │
│                           │
│          ~0 rows          │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           FILTER          │
│    ────────────────────   │
│          (x > 1)          │
│                           │
│          ~0 rows          │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│           UNNEST          │
└─────────────┬─────────────┘
┌─────────────┴─────────────┐
│      COLUMN_DATA_SCAN     │
│    ────────────────────   │
│           ~1 row          │
└───────────────────────────┘
```

## What The Library Exposes

### Core objects

The public API is centered on two types:

- `LazyFrame`: the query builder for relational operations
- `Expr`: the expression object used inside `select`, `with_columns`, `filter`, `group_by`, joins, pivots, windows, and aggregations

### Constructors

You can create a `LazyFrame` from multiple sources: Python objects, NumPy arrays, Any DataFrame/LazyFrame convertible by narwhals, DuckDB relations, tables, and DuckDB table functions.

### Frame operations

`LazyFrame` already covers a solid set of day-to-day lazy operations, including:

- projection and derived columns with `select()` and `with_columns()`
- filtering with boolean expressions or named constraints
- sorting, limiting, slicing, renaming, dropping, casting, and exploding
- joins
- grouped aggregations and `group_by_all()`
- pivots and unpivots
- schema inspection with `collect_schema()`
- SQL inspection with `sql_query()` and plan inspection with `explain()`
- export helpers such as `sink_csv()`, `sink_parquet()`, and `sink_ndjson()`

### Expression helpers

At the module level, `pql` exposes the usual expression entry points:

- `col()` and `lit()`
- `when(...).then(...).otherwise(...)`
- `coalesce()`
- scalar aggregations such as `sum`, `mean`, `median`, `min`, `max`, `len`
- horizontal aggregations such as `sum_horizontal`, `mean_horizontal`, `min_horizontal`, `max_horizontal`, `all_horizontal`, `any_horizontal`

### Expression namespaces

`Expr` exposes namespaces for both Polars-like workflows and DuckDB-oriented features:

- `.str` for strings
- `.list` for list operations
- `.arr` for DuckDB array operations
- `.struct` for structs
- `.dt` for datetime operations
- `.json` for JSON functions
- `.re` for regex operations
- `.map` for map operations
- `.enum` for DuckDB enums
- `.geo` for DuckDB geospatial functions
- `.name` for alias and naming transforms

### Selectors

`pql.selectors` provides a selectors API similar in spirit to Polars selectors, with support for:

- all columns
- name-based selection and exclusion
- string pattern-based selection
- dtype-oriented selectors
- composition of selectors inside frame operations

### Datatypes

`pql` exposes public datatype objects such as:

- `Int*`, `UInt*`, `Float*`, `Boolean`, `String`, `Date`, `Datetime`, `Duration`
- `List`, `Array`, `Struct`, `Map`, `Json`, `Enum`
- `Geometry`

Those objects are used for explicit casts and schema work while staying aligned with DuckDB types.

## Notable Features

### 1. DuckDB-native function coverage

`pql` currently exposes 200+ DuckDB-backed expression methods.

That matters because it lets you keep a fluent dataframe style while still reaching deep parts of DuckDB's function surface.

### 2. Native geometry support

DuckDB ships geometry types and functions, and `pql` exposes them directly.

That includes:

- the public `Geometry` datatype
- a `.geo` namespace on expressions
- a large set of spatial functions

This is one of the clearest areas where `pql` goes beyond plain Polars parity.

### 4. `group_by_all()`

DuckDB supports `GROUP BY ALL`, and `pql` exposes it as `LazyFrame.group_by_all()`.

If you work with DuckDB regularly, this is much nicer than forcing everything through a Polars-only mental model.

### 5. Pyochain integration

Many APIs that would normally return plain Python iterables return `pyochain` objects instead.

That means you can keep chaining operations instead of falling back to ad-hoc list manipulation.

```python
import pql

lf = pql.LazyFrame({"price": [1, 2, 3], "name": ["x", "y", "z"]})

cols = lf.columns.iter().filter(lambda col: col.startswith("p"))
result = lf.select(cols).columns
print(result)

# PyoKeysView(Dict('price': DataType(this=DType.INT, nested=False)))
```

## Differences Vs Polars

`pql` aims to be close to Polars where that makes sense, but it does not force perfect behavioral parity when DuckDB semantics differ.

For the exhaustive method-by-method matrix, see [API_COVERAGE.md](API_COVERAGE.md).

### Structural differences

- There is no eager `DataFrame` type in `pql`. The library is lazy-only.
- `LazyFrame.collect()` and `LazyFrame.lazy()` convert back to native Polars objects.
- `join(how="cross")` does not exist. Use `join_cross()` instead.

### DuckDB-driven differences

- `Categorical` is not supported because it does not map cleanly to DuckDB.
- logical operators follow SQL semantics, not Polars' integer-bitwise behavior
- null handling, ordering behavior, and some aggregation semantics follow DuckDB first
- some APIs expose DuckDB concepts directly instead of hiding them behind Polars-shaped signatures

### API shape differences

Some methods exist with deliberately different signatures because `pql` prefers a clean DuckDB-oriented surface over full Polars argument compatibility.

Examples include:

- `collect()`
- `explain()`
- `group_by()`
- `join()` and `join_asof()`
- `pivot()`
- `unique()`
- `with_row_index()`

### Current gaps

`pql` is not feature-complete relative to Polars yet. Notable missing areas include:

- async collection and streaming sinks
- several serialization helpers
- a number of expression methods and namespace methods still tracked in the coverage report
- some higher-level convenience APIs that exist in Polars but are not implemented yet

## Additions And DuckDB-Specific Strengths

Compared to Polars, `pql` is interesting not only because of what it matches, but because of what it exposes that Polars does not treat as a core target.

### DuckDB table functions and catalog access

Because `pql` can start from DuckDB tables and table functions directly, it works well for database introspection workflows.

```python
import pql

(
    pql.meta.functions()
    .filter(pql.col("function_name").str.contains("json"))
    .select("function_name", "parameter_types", "return_type")
    .sort("function_name")
    .limit(3)
    .show()
)

# ┌───────────────┬────────────────────┬─────────────┐
# │ function_name │  parameter_types   │ return_type │
# │    varchar    │     varchar[]      │   varchar   │
# ├───────────────┼────────────────────┼─────────────┤
# │ array_to_json │ []                 │ JSON        │
# │ from_json     │ [VARCHAR, VARCHAR] │ ANY         │
# │ from_json     │ [JSON, VARCHAR]    │ ANY         │
# └───────────────┴────────────────────┴─────────────┘
```

### Better fit when DuckDB is the target, not just a backend

If DuckDB is your main target, `pql` is built to keep that focus in the public API.

## Comparison With Other Tools

The relevant question is not “which library is best?”, but “which one is optimized for the workflow you actually want?”.

| Tool | Main goal | Syntax bias | Backend strategy | Best fit |
| --- | --- | --- | --- | --- |
| `pql` | Polars-like lazy API for DuckDB | Polars-like | DuckDB-first | You want DuckDB features with Polars ergonomics |
| Narwhals | portable dataframe compatibility layer | Polars-inspired | multi-backend | You write library code or want broad backend portability |
| SQLFrame | PySpark DataFrame API on SQL engines | Spark/PySpark | multi-engine SQL execution | You want PySpark-style code without Spark clusters |
| Ibis | portable dataframe expression system | Ibis-native | multi-backend | You want one API across many engines and data systems |

### Narwhals

Narwhals is primarily a compatibility layer for library authors who want one dataframe-facing API across multiple backends.

It also has a `narwhals.sql` module, so it can be used to generate DuckDB SQL with a Polars-like style. That makes it relevant here, but this is still a narrower SQL-oriented surface built around portability.

`pql` is closer to a dedicated DuckDB query library:

- it is designed specifically for DuckDB
- it exposes more DuckDB-specific functionality in the public API
- it targets a broader DuckDB-oriented surface than Narwhals' SQL layer

### SQLFrame

SQLFrame implements the PySpark DataFrame API on top of SQL engines.

That is a very different ergonomic target:

- if you think in Spark, SQLFrame is the natural comparison
- if you think in Polars, `pql` is a much closer fit

### Ibis

Ibis is a mature multi-backend expression system with support for many engines and a strong SQL compilation story.

Its value proposition is portability and backend independence. `pql` is narrower and more opinionated:

- Ibis gives you one Spark-like API for many backends
- `pql` gives you a Polars-like API specifically optimized around DuckDB as the execution target

If you need to move the same query graph between DuckDB, BigQuery, Spark, and others, Ibis is built for that. If you know you want DuckDB and want something closer to Polars, `pql` is the more direct fit.

## Current Maturity

`pql` is still a work in progress. The project tracks parity explicitly in [API_COVERAGE.md](API_COVERAGE.md).

- the library is already useful for real lazy DuckDB work
- it is not yet a drop-in Polars replacement
- the main direction is still to widen API coverage while keeping DuckDB semantics intact

## How It Works

Internally, `pql` is organized around a few clear layers:

- `LazyFrame` in `src/pql/_frame.py` builds relational queries
- `Expr` in `src/pql/_expr.py` builds expression trees
- `sqlglot` is used as the AST layer for query and expression composition
- `ScanSource` in `src/pql/_scans.py` bridges AST queries to executable DuckDB relations
- generated code in `src/pql/_code_gen/_fns.py` exposes large parts of the DuckDB function catalog

The short version is:

1. you write dataframe-style code
2. `pql` builds `sqlglot` expressions and queries
3. those queries are materialized through DuckDB
4. results come back as native Polars objects when you collect

For a contributor-oriented architecture overview, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

If you want to contribute, start with [CONTRIBUTING.md](CONTRIBUTING.md).
