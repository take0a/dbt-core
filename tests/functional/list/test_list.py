import json
import os

from dbt.tests.util import run_dbt
from tests.functional.fixtures.happy_path_fixture import (  # noqa: F401
    happy_path_project,
    happy_path_project_files,
)

# Marker to allow some objects to skip full comparison when a full comparison is
# unlikely to improve practical test effectiveness.
ANY = object()


class TestList:
    def dir(self, value):
        return os.path.normpath(value)

    def test_packages_install_path_does_not_exist(self, happy_path_project):  # noqa: F811
        run_dbt(["list"])
        packages_install_path = "dbt_packages"

        # the packages-install-path should not be created by `dbt list`
        assert not os.path.exists(packages_install_path)

    def run_dbt_ls(self, args=None, expect_pass=True):
        full_args = ["ls"]
        if args is not None:
            full_args += args
        result = run_dbt(args=full_args, expect_pass=expect_pass)

        return result

    def assert_json_equal(self, json_str, expected):
        assert json.loads(json_str) == expected

    def expect_given_output(self, args, expectations):
        for key, values in expectations.items():
            ls_result = self.run_dbt_ls(args + ["--output", key])
            if not isinstance(values, (list, tuple)):
                values = [values]
            assert len(ls_result) == len(values)
            for got, expected in zip(ls_result, values):
                if key == "json":
                    if expected != ANY:
                        self.assert_json_equal(got, expected)
                else:
                    assert got == expected

    def expect_snapshot_output(self, happy_path_project):  # noqa: F811
        expectations = {
            "name": ["my_snapshot", "snapshot_2", "snapshot_3"],
            "selector": ["test.snapshot.my_snapshot", "test.snapshot_2", "test.snapshot_3"],
            "json": [
                {
                    "name": "my_snapshot",
                    "package_name": "test",
                    "depends_on": {"nodes": [], "macros": []},
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "snapshot",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "database": happy_path_project.database,
                        "schema": happy_path_project.test_schema,
                        "dbt_valid_to_current": None,
                        "snapshot_meta_column_names": {
                            "dbt_scd_id": None,
                            "dbt_updated_at": None,
                            "dbt_valid_from": None,
                            "dbt_valid_to": None,
                            "dbt_is_deleted": None,
                        },
                        "unique_key": "id",
                        "strategy": "timestamp",
                        "updated_at": "updated_at",
                        "full_refresh": None,
                        "target_database": None,
                        "target_schema": None,
                        "alias": None,
                        "check_cols": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                    },
                    "unique_id": "snapshot.test.my_snapshot",
                    "original_file_path": normalize("snapshots/snapshot.sql"),
                    "alias": "my_snapshot",
                    "resource_type": "snapshot",
                },
                ANY,
                ANY,
            ],
            "path": [
                self.dir("snapshots/snapshot.sql"),
                self.dir("snapshots/snapshot_2.yml"),
                self.dir("snapshots/snapshot_3.yml"),
            ],
        }
        self.expect_given_output(["--resource-type", "snapshot"], expectations)

    def expect_analyses_output(self):
        expectations = {
            "name": "a",
            "selector": "test.analysis.a",
            "json": {
                "name": "a",
                "package_name": "test",
                "depends_on": {"nodes": [], "macros": []},
                "tags": ["tag"],
                "config": {
                    "enabled": True,
                    "group": "finance",
                    "materialized": "view",
                    "post-hook": [],
                    "tags": ["tag"],
                    "pre-hook": [],
                    "quoting": {},
                    "column_types": {},
                    "persist_docs": {},
                    "full_refresh": None,
                    "on_schema_change": "ignore",
                    "on_configuration_change": "apply",
                    "database": None,
                    "schema": None,
                    "alias": None,
                    "meta": {"test": 1},
                    "unique_key": None,
                    "grants": {},
                    "packages": [],
                    "incremental_strategy": None,
                    "docs": {"node_color": "purple", "show": True},
                    "contract": {"enforced": False, "alias_types": True},
                    "event_time": None,
                    "lookback": 1,
                    "batch_size": None,
                    "begin": None,
                    "concurrent_batches": None,
                },
                "unique_id": "analysis.test.a",
                "original_file_path": normalize("analyses/a.sql"),
                "alias": "a",
                "resource_type": "analysis",
            },
            "path": self.dir("analyses/a.sql"),
        }
        self.expect_given_output(["--resource-type", "analysis"], expectations)

    def expect_model_output(self):
        expectations = {
            "name": (
                "ephemeral",
                "incremental",
                "inner",
                "metricflow_time_spine",
                "metricflow_time_spine_second",
                "model_to_unit_test",
                "model_with_lots_of_schema_configs",
                "outer",
                "snapshot_source",
            ),
            "selector": (
                "test.ephemeral",
                "test.incremental",
                "test.sub.inner",
                "test.metricflow_time_spine",
                "test.metricflow_time_spine_second",
                "test.model_to_unit_test",
                "test.model_with_lots_of_schema_configs",
                "test.outer",
                "test.snapshot_source",
            ),
            "json": (
                {
                    "name": "ephemeral",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": [],
                        "macros": ["macro.dbt.current_timestamp", "macro.dbt.date_trunc"],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "ephemeral",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/ephemeral.sql"),
                    "unique_id": "model.test.ephemeral",
                    "alias": "ephemeral",
                    "resource_type": "model",
                },
                {
                    "name": "incremental",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": ["seed.test.seed"],
                        "macros": ["macro.dbt.is_incremental"],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "incremental",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": "delete+insert",
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/incremental.sql"),
                    "unique_id": "model.test.incremental",
                    "alias": "incremental",
                    "resource_type": "model",
                },
                {
                    "name": "inner",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": ["model.test.outer"],
                        "macros": [],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "view",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/sub/inner.sql"),
                    "unique_id": "model.test.inner",
                    "alias": "inner",
                    "resource_type": "model",
                },
                {
                    "name": "metricflow_time_spine",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": [],
                        "macros": ["macro.dbt.current_timestamp", "macro.dbt.date_trunc"],
                    },
                    "config": {
                        "enabled": True,
                        "group": "finance",
                        "materialized": "view",
                        "post-hook": [
                            {
                                "sql": "SELECT 'string_post_hook' as my_post_hook;",
                                "transaction": True,
                                "index": None,
                            }
                        ],
                        "tags": ["list", "of", "tags"],
                        "pre-hook": [
                            {
                                "sql": "SELECT 'string_pre_hook' as my_pre_hook;",
                                "transaction": True,
                                "index": None,
                            }
                        ],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/metricflow_time_spine.sql"),
                    "unique_id": "model.test.metricflow_time_spine",
                    "alias": "metricflow_time_spine",
                    "resource_type": "model",
                    "tags": ["list", "of", "tags"],
                },
                {
                    "name": "metricflow_time_spine_second",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": [],
                        "macros": ["macro.dbt.current_timestamp", "macro.dbt.date_trunc"],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "view",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": "ts_second",
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/metricflow_time_spine_second.sql"),
                    "unique_id": "model.test.metricflow_time_spine_second",
                    "alias": "metricflow_time_spine_second",
                    "resource_type": "model",
                },
                {
                    "alias": "model_to_unit_test",
                    "config": {
                        "access": "protected",
                        "alias": None,
                        "batch_size": None,
                        "begin": None,
                        "column_types": {},
                        "concurrent_batches": None,
                        "contract": {"alias_types": True, "enforced": False},
                        "database": None,
                        "docs": {"node_color": None, "show": True},
                        "enabled": True,
                        "event_time": None,
                        "freshness": None,
                        "full_refresh": None,
                        "grants": {},
                        "group": None,
                        "incremental_strategy": None,
                        "lookback": 1,
                        "materialized": "table",
                        "meta": {},
                        "on_configuration_change": "apply",
                        "on_schema_change": "ignore",
                        "packages": [],
                        "persist_docs": {},
                        "post-hook": [],
                        "pre-hook": [],
                        "quoting": {},
                        "schema": None,
                        "tags": [],
                        "unique_key": None,
                    },
                    "depends_on": {"macros": [], "nodes": ["seed.test.seed"]},
                    "name": "model_to_unit_test",
                    "original_file_path": normalize("models/model_to_unit_test.sql"),
                    "package_name": "test",
                    "resource_type": "model",
                    "tags": [],
                    "unique_id": "model.test.model_to_unit_test",
                },
                {
                    "name": "model_with_lots_of_schema_configs",
                    "resource_type": "model",
                    "package_name": "test",
                    "original_file_path": normalize(
                        "models/model_with_lots_of_schema_configs.sql"
                    ),
                    "unique_id": "model.test.model_with_lots_of_schema_configs",
                    "alias": "outer_alias",
                    "config": {
                        "enabled": True,
                        "access": "public",
                        "alias": "outer_alias",
                        "schema": "test",
                        "sql_header": "SELECT 1 as header;",
                        "database": "dbt",
                        "docs": {"node_color": "purple", "show": True},
                        "event_time": None,
                        "tags": ["string_tag"],
                        "meta": {"my_custom_property": "string_meta"},
                        "group": None,
                        "materialized": "table",
                        "incremental_strategy": None,
                        "batch_size": "day",
                        "lookback": 5,
                        "begin": "2020-01-01",
                        "persist_docs": {"columns": True, "relation": True},
                        "post-hook": [
                            {
                                "sql": "SELECT 'string_post_hook' as my_post_hook;",
                                "transaction": True,
                                "index": None,
                            }
                        ],
                        "pre-hook": [
                            {
                                "sql": "SELECT 'string_pre_hook' as my_pre_hook;",
                                "transaction": True,
                                "index": None,
                            }
                        ],
                        "quoting": {},
                        "column_types": {},
                        "concurrent_batches": False,
                        "contract": {"alias_types": True, "enforced": False},
                        "full_refresh": False,
                        "unique_key": "id",
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "grants": {"select": ["root"]},
                        "packages": [],
                        "freshness": None,
                    },
                    "depends_on": {
                        "macros": [],
                        "nodes": ["source.test.my_source.my_table", "model.test.ephemeral"],
                    },
                    "tags": ["string_tag"],
                },
                {
                    "name": "outer",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": ["model.test.ephemeral"],
                        "macros": [],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "view",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "unique_key": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "contract": {"enforced": False, "alias_types": True},
                        "access": "protected",
                        "event_time": None,
                        "lookback": 1,
                        "batch_size": None,
                        "begin": None,
                        "concurrent_batches": None,
                        "freshness": None,
                    },
                    "original_file_path": normalize("models/outer.sql"),
                    "unique_id": "model.test.outer",
                    "alias": "outer",
                    "resource_type": "model",
                },
                ANY,
            ),
            "path": (
                self.dir("models/ephemeral.sql"),
                self.dir("models/incremental.sql"),
                self.dir("models/sub/inner.sql"),
                self.dir("models/metricflow_time_spine.sql"),
                self.dir("models/metricflow_time_spine_second.sql"),
                self.dir("models/model_to_unit_test.sql"),
                self.dir("models/model_with_lots_of_schema_configs.sql"),
                self.dir("models/outer.sql"),
                self.dir("models/snapshot_source.sql"),
            ),
        }

        self.expect_given_output(["--resource-type", "model"], expectations)

    # Do not include ephemeral model - it was not selected
    def expect_model_ephemeral_output(self):
        expectations = {
            "name": ("outer"),
            "selector": ("test.outer"),
            "json": (
                {
                    "name": "outer",
                    "package_name": "test",
                    "depends_on": {"nodes": [], "macros": []},
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "materialized": "view",
                        "post-hook": [],
                        "tags": [],
                        "pre-hook": [],
                        "quoting": {},
                        "column_types": {},
                        "persist_docs": {},
                        "full_refresh": None,
                        "on_schema_change": "ignore",
                        "on_configuration_change": "apply",
                        "database": None,
                        "schema": None,
                        "alias": None,
                        "meta": {},
                        "grants": {},
                        "packages": [],
                        "incremental_strategy": None,
                        "docs": {"node_color": None, "show": True},
                        "access": "protected",
                    },
                    "unique_id": "model.test.ephemeral",
                    "original_file_path": normalize("models/ephemeral.sql"),
                    "alias": "outer",
                    "resource_type": "model",
                },
            ),
            "path": (self.dir("models/outer.sql"),),
        }
        self.expect_given_output(["--model", "outer"], expectations)

    def expect_source_output(self):
        expectations = {
            "name": "my_source.my_table",
            "selector": "source:test.my_source.my_table",
            "json": {
                "config": {
                    "enabled": True,
                    "event_time": "column_name",
                    "freshness": {
                        "error_after": {
                            "count": 2,
                            "period": "hour",
                        },
                        "warn_after": {
                            "count": 1,
                            "period": "minute",
                        },
                        "filter": "column_name = 1",
                    },
                    "meta": {"test": 1},
                    "tags": ["tag"],
                },
                "unique_id": "source.test.my_source.my_table",
                "original_file_path": normalize("models/schema.yml"),
                "package_name": "test",
                "name": "my_table",
                "source_name": "my_source",
                "resource_type": "source",
                "tags": [],
            },
            "path": self.dir("models/schema.yml"),
        }
        # should we do this --select automatically for a user if if 'source' is
        # in the resource types and there is no '--select' or '--exclude'?
        self.expect_given_output(
            ["--resource-type", "source", "--select", "source:*"], expectations
        )

    def expect_seed_output(self):
        expectations = {
            "name": "seed",
            "selector": "test.seed",
            "json": {
                "name": "seed",
                "package_name": "test",
                "tags": ["tag"],
                "config": {
                    "enabled": True,
                    "group": "finance",
                    "materialized": "seed",
                    "post-hook": [{"sql": "select 1", "transaction": True, "index": None}],
                    "tags": ["tag"],
                    "pre-hook": [{"sql": "select 1", "transaction": True, "index": None}],
                    "quoting": {},
                    "column_types": {"a": "BIGINT"},
                    "delimiter": ",",
                    "persist_docs": {},
                    "quote_columns": False,
                    "full_refresh": True,
                    "unique_key": None,
                    "on_schema_change": "ignore",
                    "on_configuration_change": "apply",
                    "database": "dbt",
                    "schema": "test",
                    "alias": "test_alias",
                    "meta": {"meta_key": "meta_value"},
                    "grants": {},
                    "packages": [],
                    "incremental_strategy": None,
                    "docs": {"node_color": "purple", "show": True},
                    "contract": {"enforced": False, "alias_types": True},
                    "event_time": "my_time_field",
                    "lookback": 1,
                    "batch_size": None,
                    "begin": None,
                    "concurrent_batches": None,
                },
                "depends_on": {"macros": []},
                "unique_id": "seed.test.seed",
                "original_file_path": normalize("seeds/seed.csv"),
                "alias": "test_alias",
                "resource_type": "seed",
            },
            "path": self.dir("seeds/seed.csv"),
        }
        self.expect_given_output(["--resource-type", "seed"], expectations)

    def expect_test_output(self):
        # This is order sensitive :grimace:
        expectations = {
            "name": (
                "expression_is_true_seed_b_2",
                "my_favorite_test",
                "my_second_favorite_test",
                "not_null_outer_id",
                "not_null_seed__a_",
                "not_null_seed__b_",
                "t",
                "unique_model_with_lots_of_schema_configs_id",
                "unique_outer_id",
            ),
            "selector": (
                "test.expression_is_true_seed_b_2",
                "test.my_favorite_test",
                "test.my_second_favorite_test",
                "test.not_null_outer_id",
                "test.not_null_seed__a_",
                "test.not_null_seed__b_",
                "test.t",
                "test.unique_model_with_lots_of_schema_configs_id",
                "test.unique_outer_id",
            ),
            "json": (
                {
                    "alias": "expression_is_true_seed_b_2",
                    "config": {
                        "alias": None,
                        "database": None,
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": None,
                        "limit": None,
                        "materialized": "test",
                        "meta": {},
                        "schema": "dbt_test__audit",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        "tags": [],
                        "warn_if": "!= 0",
                        "where": None,
                    },
                    "depends_on": {
                        "macros": [
                            "macro.test.test_expression_is_true",
                            "macro.dbt.get_where_subquery",
                        ],
                        "nodes": ["seed.test.seed"],
                    },
                    "name": "expression_is_true_seed_b_2",
                    "original_file_path": normalize("seeds/s.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": [],
                    "unique_id": "test.test.expression_is_true_seed_b_2.4e0babbea4",
                },
                {
                    "alias": "not_null__id__alias",
                    "config": {
                        "alias": "not_null__id__alias",
                        "database": "dbt",
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": "important_tests",
                        "limit": 10,
                        "materialized": "test",
                        "meta": {"my_custom_meta_key": "my_custom_meta_value"},
                        "schema": "dbt_test__audit",
                        "severity": "warn",
                        "store_failures": True,
                        "store_failures_as": "table",
                        "tags": ["test_tag"],
                        "warn_if": "!= 0",
                        "where": "1 = 1",
                    },
                    "depends_on": {
                        "macros": ["macro.dbt.test_not_null"],
                        "nodes": ["model.test.model_with_lots_of_schema_configs"],
                    },
                    "name": "my_favorite_test",
                    "original_file_path": normalize("models/schema.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": ["test_tag"],
                    "unique_id": "test.test.my_favorite_test.b488d63233",
                },
                {
                    "alias": "my_generic_test__created_at__alias",
                    "config": {
                        "alias": "my_generic_test__created_at__alias",
                        "database": "dbt",
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": "important_tests",
                        "limit": 10,
                        "materialized": "test",
                        "meta": {"my_custom_meta_key": "my_custom_meta_value"},
                        "schema": "dbt_test__audit",
                        "severity": "warn",
                        "store_failures": True,
                        "store_failures_as": "table",
                        "tags": ["test_tag", "test_tag"],
                        "warn_if": "!= 0",
                        "where": "1 = 1",
                    },
                    "depends_on": {
                        "macros": [
                            "macro.test.test_my_generic_test",
                            "macro.dbt.get_where_subquery",
                        ],
                        "nodes": ["model.test.model_with_lots_of_schema_configs"],
                    },
                    "name": "my_second_favorite_test",
                    "original_file_path": normalize("models/schema.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": ["test_tag"],
                    "unique_id": "test.test.my_second_favorite_test.c8955109ad",
                },
                {
                    "name": "not_null_outer_id",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": ["model.test.outer"],
                        "macros": ["macro.dbt.test_not_null"],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "test",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        "warn_if": "!= 0",
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "where": None,
                        "limit": None,
                        "tags": [],
                        "database": None,
                        "schema": "dbt_test__audit",
                        "alias": None,
                        "meta": {},
                    },
                    "unique_id": "test.test.not_null_outer_id.a226f4fb36",
                    "original_file_path": normalize("models/schema.yml"),
                    "alias": "not_null_outer_id",
                    "resource_type": "test",
                },
                {
                    "alias": "not_null_seed__a_",
                    "config": {
                        "alias": None,
                        "database": None,
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": None,
                        "limit": None,
                        "materialized": "test",
                        "meta": {},
                        "schema": "dbt_test__audit",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        # generic test builders don't propagate tags correctly
                        "tags": [],
                        "warn_if": "!= 0",
                        "where": None,
                    },
                    "depends_on": {
                        "macros": ["macro.dbt.test_not_null"],
                        "nodes": ["seed.test.seed"],
                    },
                    "name": "not_null_seed__a_",
                    "original_file_path": normalize("seeds/s.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": [],
                    "unique_id": "test.test.not_null_seed__a_.6b59640cde",
                },
                {
                    "alias": "not_null_seed__b_",
                    "config": {
                        "alias": None,
                        "database": None,
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": None,
                        "limit": None,
                        "materialized": "test",
                        "meta": {},
                        "schema": "dbt_test__audit",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        # generic test builders don't propagate tags correctly
                        "tags": [],
                        "warn_if": "!= 0",
                        "where": None,
                    },
                    "depends_on": {
                        "macros": ["macro.dbt.test_not_null"],
                        "nodes": ["seed.test.seed"],
                    },
                    "name": "not_null_seed__b_",
                    "original_file_path": normalize("seeds/s.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": [],
                    "unique_id": "test.test.not_null_seed__b_.a088b263cb",
                },
                {
                    "name": "t",
                    "package_name": "test",
                    "alias": "test_alias",
                    "config": {
                        "alias": "test_alias",
                        "database": "dbt",
                        "docs": {"node_color": "blue", "show": True},
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": "important_tests",
                        "limit": 10,
                        "materialized": "test",
                        "meta": {"my_custom_meta_key": "my_custom_meta_value"},
                        "schema": "dbt_test__audit",
                        "severity": "warn",
                        "store_failures": True,
                        "store_failures_as": "table",
                        "tags": ["test_tag"],
                        "warn_if": "!= 0",
                        "where": "1 = 1",
                    },
                    "depends_on": {"macros": [], "nodes": []},
                    "name": "t",
                    "original_file_path": normalize("tests/t.sql"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": ["test_tag"],
                    "unique_id": "test.test.t",
                },
                {
                    "alias": "unique_model_with_lots_of_schema_configs_id",
                    "config": {
                        "alias": None,
                        "database": None,
                        "enabled": True,
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "group": None,
                        "limit": None,
                        "materialized": "test",
                        "meta": {},
                        "schema": "dbt_test__audit",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        "tags": [],
                        "warn_if": "!= 0",
                        "where": None,
                    },
                    "depends_on": {
                        "macros": ["macro.dbt.test_unique"],
                        "nodes": ["model.test.model_with_lots_of_schema_configs"],
                    },
                    "name": "unique_model_with_lots_of_schema_configs_id",
                    "original_file_path": normalize("models/schema.yml"),
                    "package_name": "test",
                    "resource_type": "test",
                    "tags": [],
                    "unique_id": "test.test.unique_model_with_lots_of_schema_configs_id.8328d84982",
                },
                {
                    "name": "unique_outer_id",
                    "package_name": "test",
                    "depends_on": {
                        "nodes": ["model.test.outer"],
                        "macros": ["macro.dbt.test_unique"],
                    },
                    "tags": [],
                    "config": {
                        "enabled": True,
                        "group": None,
                        "materialized": "test",
                        "severity": "ERROR",
                        "store_failures": None,
                        "store_failures_as": None,
                        "warn_if": "!= 0",
                        "error_if": "!= 0",
                        "fail_calc": "count(*)",
                        "where": None,
                        "limit": None,
                        "tags": [],
                        "database": None,
                        "schema": "dbt_test__audit",
                        "alias": None,
                        "meta": {},
                    },
                    "unique_id": "test.test.unique_outer_id.2195e332d3",
                    "original_file_path": normalize("models/schema.yml"),
                    "alias": "unique_outer_id",
                    "resource_type": "test",
                },
            ),
            "path": (
                self.dir("seeds/s.yml"),
                self.dir("models/schema.yml"),
                self.dir("models/schema.yml"),
                self.dir("models/schema.yml"),
                self.dir("seeds/s.yml"),
                self.dir("seeds/s.yml"),
                self.dir("tests/t.sql"),
                self.dir("models/schema.yml"),
                self.dir("models/schema.yml"),
            ),
        }
        self.expect_given_output(["--resource-type", "test"], expectations)

    def expect_all_output(self):
        # generic test FQNS include the resource + column they're defined on
        # models are just package, subdirectory path, name
        # sources are like models, ending in source_name.table_name
        expected_default = {
            "exposure:test.weekly_jaffle_metrics",
            "test.ephemeral",
            "test.incremental",
            "test.snapshot.my_snapshot",
            "test.snapshot_2",
            "test.snapshot_3",
            "test.sub.inner",
            "test.outer",
            "test.snapshot_source",
            "test.seed",
            "source:test.my_source.my_table",
            "test.not_null_outer_id",
            "test.unique_outer_id",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "test.unique_model_with_lots_of_schema_configs_id",
            "test.t",
            "test.my_favorite_test",
            "test.my_second_favorite_test",
            "semantic_model:test.my_sm",
            "metric:test.total_outer",
            "saved_query:test.my_saved_query",
            "test.expression_is_true_seed_b_2",
            "test.not_null_seed__a_",
            "test.not_null_seed__b_",
            "unit_test:test.test_model_to_unit_test",
            "unit_test:test.test_model_to_unit_test_2",
        }
        # analyses have their type inserted into their fqn like tests
        expected_all = expected_default | {"test.analysis.a"}

        results = self.run_dbt_ls(["--resource-type", "all", "--select", "*", "source:*"])
        assert set(results) == expected_all

        results = self.run_dbt_ls(["--select", "*", "source:*"])
        assert set(results) == expected_default

        results = self.run_dbt_ls(["--resource-type", "default", "--select", "*", "source:*"])
        assert set(results) == expected_default

        results = self.run_dbt_ls

    def expect_select(self):
        results = self.run_dbt_ls(["--resource-type", "test", "--select", "outer"])
        assert set(results) == {"test.not_null_outer_id", "test.unique_outer_id"}

        self.run_dbt_ls(["--resource-type", "test", "--select", "inner"], expect_pass=True)

        results = self.run_dbt_ls(["--resource-type", "test", "--select", "+inner"])
        assert set(results) == {"test.not_null_outer_id", "test.unique_outer_id"}

        results = self.run_dbt_ls(["--resource-type", "semantic_model"])
        assert set(results) == {"semantic_model:test.my_sm"}

        results = self.run_dbt_ls(["--resource-type", "metric"])
        assert set(results) == {"metric:test.total_outer"}

        results = self.run_dbt_ls(["--resource-type", "saved_query"])
        assert set(results) == {"saved_query:test.my_saved_query"}

        results = self.run_dbt_ls(["--resource-type", "model", "--select", "outer+"])
        assert set(results) == {"test.outer", "test.sub.inner"}

        results = self.run_dbt_ls(["--resource-type", "model", "--exclude", "inner"])
        assert set(results) == {
            "test.ephemeral",
            "test.outer",
            "test.snapshot_source",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "test.incremental",
        }

        results = self.run_dbt_ls(["--select", "config.incremental_strategy:delete+insert"])
        assert set(results) == {"test.incremental"}

        self.run_dbt_ls(
            ["--select", "config.incremental_strategy:insert_overwrite"], expect_pass=True
        )

    def expect_resource_type_multiple(self):
        """Expect selected resources when --resource-type given multiple times"""
        results = self.run_dbt_ls(["--resource-type", "test", "--resource-type", "model"])
        assert set(results) == {
            "test.ephemeral",
            "test.incremental",
            "test.not_null_outer_id",
            "test.outer",
            "test.snapshot_source",
            "test.sub.inner",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "test.t",
            "test.unique_outer_id",
            "test.unique_model_with_lots_of_schema_configs_id",
            "test.expression_is_true_seed_b_2",
            "test.not_null_seed__a_",
            "test.not_null_seed__b_",
            "test.my_favorite_test",
            "test.my_second_favorite_test",
        }

        results = self.run_dbt_ls(
            [
                "--resource-type",
                "test",
                "--resource-type",
                "model",
                "--exclude",
                "unique_outer_id",
            ]
        )
        assert set(results) == {
            "test.ephemeral",
            "test.incremental",
            "test.not_null_outer_id",
            "test.outer",
            "test.snapshot_source",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "test.sub.inner",
            "test.t",
            "test.unique_model_with_lots_of_schema_configs_id",
            "test.expression_is_true_seed_b_2",
            "test.not_null_seed__a_",
            "test.not_null_seed__b_",
            "test.my_favorite_test",
            "test.my_second_favorite_test",
        }

        results = self.run_dbt_ls(
            [
                "--resource-type",
                "test",
                "model",
                "--select",
                "+inner",
                "outer+",
                "--exclude",
                "inner",
            ]
        )
        assert set(results) == {
            "test.ephemeral",
            "test.not_null_outer_id",
            "test.unique_outer_id",
            "test.outer",
        }

    def expect_resource_type_env_var(self):
        """Expect selected resources when --resource-type given multiple times"""
        os.environ["DBT_RESOURCE_TYPES"] = "test model"
        results = self.run_dbt_ls()
        assert set(results) == {
            "test.ephemeral",
            "test.incremental",
            "test.not_null_outer_id",
            "test.outer",
            "test.snapshot_source",
            "test.sub.inner",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "test.t",
            "test.unique_outer_id",
            "test.unique_model_with_lots_of_schema_configs_id",
            "test.expression_is_true_seed_b_2",
            "test.not_null_seed__a_",
            "test.not_null_seed__b_",
            "test.my_favorite_test",
            "test.my_second_favorite_test",
        }
        del os.environ["DBT_RESOURCE_TYPES"]
        os.environ["DBT_EXCLUDE_RESOURCE_TYPES"] = (
            "test saved_query metric source semantic_model snapshot seed"
        )
        results = self.run_dbt_ls()
        assert set(results) == {
            "exposure:test.weekly_jaffle_metrics",
            "test.ephemeral",
            "test.incremental",
            "test.outer",
            "test.snapshot_source",
            "test.sub.inner",
            "test.metricflow_time_spine",
            "test.metricflow_time_spine_second",
            "test.model_to_unit_test",
            "test.model_with_lots_of_schema_configs",
            "unit_test:test.test_model_to_unit_test",
            "unit_test:test.test_model_to_unit_test_2",
        }
        del os.environ["DBT_EXCLUDE_RESOURCE_TYPES"]

    def expect_selected_keys(self, happy_path_project):  # noqa: F811
        """Expect selected fields of the the selected model"""
        expectations = [
            {
                "database": happy_path_project.database,
                "schema": happy_path_project.test_schema,
                "alias": "inner",
            }
        ]
        results = self.run_dbt_ls(
            [
                "--model",
                "inner",
                "--output",
                "json",
                "--output-keys",
                "database",
                "schema",
                "alias",
            ]
        )
        assert len(results) == len(expectations)

        for got, expected in zip(results, expectations):
            self.assert_json_equal(got, expected)

        """Expect selected fields when --output-keys given multiple times
        """
        expectations = [
            {"database": happy_path_project.database, "schema": happy_path_project.test_schema}
        ]
        results = self.run_dbt_ls(
            [
                "--model",
                "inner",
                "--output",
                "json",
                "--output-keys",
                "database",
                "--output-keys",
                "schema",
            ]
        )
        assert len(results) == len(expectations)

        for got, expected in zip(results, expectations):
            self.assert_json_equal(got, expected)

        """Expect selected fields of the test resource types
        """
        expectations = [
            {"name": "expression_is_true_seed_b_2", "column_name": None},
            {"name": "my_favorite_test", "column_name": "id"},
            {"name": "my_second_favorite_test", "column_name": "created_at"},
            {"name": "not_null_outer_id", "column_name": "id"},
            {"name": "not_null_seed__a_", "column_name": '"a"'},
            {"name": "not_null_seed__b_", "column_name": '"b"'},
            {"name": "t"},
            {"name": "unique_model_with_lots_of_schema_configs_id", "column_name": "id"},
            {"name": "unique_outer_id", "column_name": "id"},
        ]
        results = self.run_dbt_ls(
            [
                "--resource-type",
                "test",
                "--output",
                "json",
                "--output-keys",
                "name",
                "column_name",
            ]
        )
        assert len(results) == len(expectations)

        for got, expected in zip(
            sorted(results, key=lambda x: json.loads(x).get("name")),
            sorted(expectations, key=lambda x: x.get("name")),
        ):
            self.assert_json_equal(got, expected)

        """Expect nothing (non-existent keys) for the selected models
        """
        expectations = [{}, {}]
        results = self.run_dbt_ls(
            [
                "--model",
                "inner outer",
                "--output",
                "json",
                "--output-keys",
                "non_existent_key",
            ]
        )
        assert len(results) == len(expectations)

        for got, expected in zip(results, expectations):
            self.assert_json_equal(got, expected)

    def test_ls(self, happy_path_project):  # noqa: F811
        self.expect_snapshot_output(happy_path_project)
        self.expect_analyses_output()
        self.expect_model_output()
        self.expect_source_output()
        self.expect_seed_output()
        self.expect_test_output()
        self.expect_select()
        self.expect_resource_type_multiple()
        self.expect_resource_type_env_var()
        self.expect_all_output()
        self.expect_selected_keys(happy_path_project)


def normalize(path):
    """On windows, neither is enough on its own:
    >>> normcase('C:\\documents/ALL CAPS/subdir\\..')
    'c:\\documents\\all caps\\subdir\\..'
    >>> normpath('C:\\documents/ALL CAPS/subdir\\..')
    'C:\\documents\\ALL CAPS'
    >>> normpath(normcase('C:\\documents/ALL CAPS/subdir\\..'))
    'c:\\documents\\all caps'
    """
    return os.path.normcase(os.path.normpath(path))
