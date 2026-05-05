
# PQL, write polars syntax, create SQL queries for DuckDB

This package is **WIP** and ultimately aim to provide a polars like API for [DuckDB Python API](https://duckdb.org/docs/stable/clients/python/overview), as well as full support of the [DuckDB functions](https://duckdb.org/docs/stable/sql/functions/overview).

## Differences and additions compared to polars

Altough `pql` aims to be as close as possible to polars, some differences exists.
Sometimes they are due to hard limitations of duckdb (e.g `Categorical` datatypes), sometimes they are just deliberate design choices (e.g cross join strategy).
Some of those are listed here, but for a more comprehensive list, see the [API coverage](API_COVERAGE.md) report.

### Differences

- `DataFrame` don't exist. Only `LazyFrame` is implemented, as it is the only one that can be implemented with duckdb.
- To convert to polars, you can do:

```python
import pql

lf_pql = pql.LazyFrame({...})
lf_polars = lf_pql.lazy()  # equivalent to DuckDBPyRelation.pl(lazy=True)
df_polars = lf_pql.collect()  # equivalent to DuckDBPyRelation.pl(lazy=False)
```

- `LazyFrame.join()` don't have a `"cross"` strategy. Instead, call `LazyFrame.join_cross()`. This is a deliberate choice, because:
  - `duckdb` natively have differents methods for join/cross_join
  - The internal implementation is simpler and cleaner if we don't have to handle the cross join as a special case of the regular join
  - The public API is clearer, as *on*, *left_on* and *right_on* parameters don't make sense for a cross join, and it is better to not have them in the signature of the method, rather than throwing runtime errors if they are used with a cross join strategy.
- `Categorical` datatypes are not supported (this is not representable in duckdb).
- `Expr.{and_, or_}` methods align on `SQL` semantics, and are not bitwise operations on `Integers` like in polars.

### Additions from polars

- Full support of the `GEOMETRY` datatypes and functions, as they are [natively supported in duckdb](https://duckdb.org/docs/current/sql/data_types/geometry)
- `LazyFrame.group_by_all()` method -> [see more here](https://duckdb.org/docs/stable/sql/query_syntax/groupby#group-by-all)
- columns/schema, and other methods/properties who return plain python `Iterable` return [pyochain objects](https://outsquarecapital.github.io/pyochain/). This allows you to use all the methods of those objects, whilst keeping the same method chaining style than with `Expression/LazyFrame`. For example, you can do:

```python
>>> data = {"price": [1, 2, 3], "name": ["x", "y", "z"]}
>>> lf = pql.LazyFrame(data)
# get the columns as a pyochain object
>>> cols = lf.columns.iter().filter(lambda col: col.startswith("p"))
>>> lf.select(cols).columns
Vec("price",)

```

## Comparison to other tools

### Narwhals

[narwhals](https://github.com/narwhals-dev/narwhals) aims to support more functionnality from polars AND all of those from duckdb, as pql is not limited by multiple backend compatibility.
Furthermore, `narwhals` is primarly designed for library developpers who want integration with multiple dataframe libraries, not for end users.
Narwhals support a **subset** of polars API, hence necessarily a **subset** of DuckDB API, while pql aims to support the **full** API of both.

### SQLFrame

[SQLFrame](https://github.com/eakmanrq/sqlframe) is fundamentally a PySpark oriented library API-wise.

### Ibis

Ibis has a different syntax from polars. It can be close for some operations, but totally different for others.
Also the goal isn't the same, as Ibis is more focused on providing a high level API for multiple backends, while pql is focused on providing a polars like API for DuckDB.
