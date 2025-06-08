import logging
import re
from typing import TypeVar

import pytest

from dbt.adapters.events import types as adapter_types
from dbt.adapters.events.logging import AdapterLogger
from dbt.artifacts.schemas.results import RunStatus, TimingInfo
from dbt.artifacts.schemas.run import RunResult
from dbt.events import types as core_types
from dbt.events.base_types import (
    CoreBaseEvent,
    DebugLevel,
    DynamicLevel,
    ErrorLevel,
    InfoLevel,
    TestLevel,
    WarnLevel,
)
from dbt.task.printer import print_run_end_messages
from dbt_common.events import types
from dbt_common.events.base_types import msg_from_base_event
from dbt_common.events.event_manager import EventManager, TestEventManager
from dbt_common.events.event_manager_client import ctx_set_event_manager
from dbt_common.events.functions import msg_to_dict, msg_to_json
from dbt_common.events.helpers import get_json_string_utcnow


# takes in a class and finds any subclasses for it
def get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        if subclass not in [TestLevel, DebugLevel, WarnLevel, InfoLevel, ErrorLevel, DynamicLevel]:
            all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return set(all_subclasses)


class TestAdapterLogger:
    # this interface is documented for adapter maintainers to plug into
    # so we should test that it at the very least doesn't explode.
    def test_basic_adapter_logging_interface(self):
        logger = AdapterLogger("dbt_tests")
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.exception("exception message")
        logger.critical("exception message")

    # python loggers allow deferring string formatting via this signature:
    def test_formatting(self):
        logger = AdapterLogger("dbt_tests")
        # tests that it doesn't throw
        logger.debug("hello {}", "world")

        # enters lower in the call stack to test that it formats correctly
        event = adapter_types.AdapterEventDebug(
            name="dbt_tests", base_msg="hello {}", args=["world"]
        )
        assert "hello world" in event.message()

        # tests that it doesn't throw
        logger.debug("1 2 {}", "3")

        # enters lower in the call stack to test that it formats correctly
        event = adapter_types.AdapterEventDebug(name="dbt_tests", base_msg="1 2 {}", args=[3])
        assert "1 2 3" in event.message()

        # tests that it doesn't throw
        logger.debug("boop{x}boop")

        # enters lower in the call stack to test that it formats correctly
        # in this case it's that we didn't attempt to replace anything since there
        # were no args passed after the initial message
        event = adapter_types.AdapterEventDebug(name="dbt_tests", base_msg="boop{x}boop", args=[])
        assert "boop{x}boop" in event.message()

        # ensure AdapterLogger and subclasses makes all base_msg members
        # of type string; when someone writes logger.debug(a) where a is
        # any non-string object
        event = adapter_types.AdapterEventDebug(name="dbt_tests", base_msg=[1, 2, 3], args=[3])
        assert isinstance(event.base_msg, str)

        event = core_types.JinjaLogDebug(msg=[1, 2, 3])
        assert isinstance(event.msg, str)

    def test_set_adapter_dependency_log_level(self):
        logger = AdapterLogger("dbt_tests")
        package_log = logging.getLogger("test_package_log")
        logger.set_adapter_dependency_log_level("test_package_log", "DEBUG")
        package_log.debug("debug message")


class TestEventCodes:

    # checks to see if event codes are duplicated to keep codes singluar and clear.
    # also checks that event codes follow correct namming convention ex. E001
    def test_event_codes(self):
        all_concrete = get_all_subclasses(CoreBaseEvent)
        all_codes = set()

        for event_cls in all_concrete:
            code = event_cls.code(event_cls)
            # must be in the form 1 capital letter, 3 digits
            assert re.match("^[A-Z][0-9]{3}", code)
            # cannot have been used already
            assert (
                code not in all_codes
            ), f"{code} is assigned more than once. Check types.py for duplicates."
            all_codes.add(code)


sample_values = [
    # N.B. Events instantiated here include the module prefix in order to
    # avoid having the entire list twice in the code.
    # A - pre-project loading
    core_types.MainReportVersion(version=""),
    core_types.MainReportArgs(args={}),
    core_types.MainTrackingUserState(user_state=""),
    core_types.MissingProfileTarget(profile_name="", target_name=""),
    core_types.InvalidOptionYAML(option_name="vars"),
    core_types.LogDbtProjectError(),
    core_types.LogDbtProfileError(),
    core_types.StarterProjectPath(dir=""),
    core_types.ConfigFolderDirectory(dir=""),
    core_types.NoSampleProfileFound(adapter=""),
    core_types.ProfileWrittenWithSample(name="", path=""),
    core_types.ProfileWrittenWithTargetTemplateYAML(name="", path=""),
    core_types.ProfileWrittenWithProjectTemplateYAML(name="", path=""),
    core_types.SettingUpProfile(),
    core_types.InvalidProfileTemplateYAML(),
    core_types.ProjectNameAlreadyExists(name=""),
    core_types.ProjectCreated(project_name=""),
    # D - Deprecations ======================
    core_types.PackageRedirectDeprecation(old_name="", new_name=""),
    core_types.PackageInstallPathDeprecation(),
    core_types.ConfigSourcePathDeprecation(deprecated_path="", exp_path=""),
    core_types.ConfigDataPathDeprecation(deprecated_path="", exp_path=""),
    adapter_types.AdapterDeprecationWarning(old_name="", new_name=""),
    core_types.MetricAttributesRenamed(metric_name=""),
    core_types.ExposureNameDeprecation(exposure=""),
    core_types.InternalDeprecation(name="", reason="", suggested_action="", version=""),
    core_types.EnvironmentVariableRenamed(old_name="", new_name=""),
    core_types.ConfigLogPathDeprecation(deprecated_path=""),
    core_types.ConfigTargetPathDeprecation(deprecated_path=""),
    adapter_types.CollectFreshnessReturnSignature(),
    core_types.TestsConfigDeprecation(deprecated_path="", exp_path=""),
    core_types.ProjectFlagsMovedDeprecation(),
    core_types.SpacesInResourceNameDeprecation(unique_id="", level=""),
    core_types.ResourceNamesWithSpacesDeprecation(
        count_invalid_names=1, show_debug_hint=True, level=""
    ),
    core_types.PackageMaterializationOverrideDeprecation(
        package_name="my_package", materialization_name="view"
    ),
    core_types.SourceFreshnessProjectHooksNotRun(),
    core_types.MFTimespineWithoutYamlConfigurationDeprecation(),
    core_types.MFCumulativeTypeParamsDeprecation(),
    core_types.MicrobatchMacroOutsideOfBatchesDeprecation(),
    core_types.GenericJSONSchemaValidationDeprecation(violation="", key_path="", file=""),
    core_types.UnexpectedJinjaBlockDeprecation(msg="", file=""),
    core_types.DuplicateYAMLKeysDeprecation(duplicate_description="", file=""),
    core_types.CustomTopLevelKeyDeprecation(msg="", file=""),
    core_types.CustomKeyInConfigDeprecation(key="", key_path="", file=""),
    core_types.CustomKeyInObjectDeprecation(key="", key_path="", file=""),
    core_types.DeprecationsSummary(summaries=[], show_all_hint=True),
    core_types.CustomOutputPathInSourceFreshnessDeprecation(path=""),
    core_types.PropertyMovedToConfigDeprecation(key="", key_path="", file=""),
    core_types.WEOIncludeExcludeDeprecation(found_include=True, found_exclude=True),
    # E - DB Adapter ======================
    adapter_types.AdapterEventDebug(),
    adapter_types.AdapterEventInfo(),
    adapter_types.AdapterEventWarning(),
    adapter_types.AdapterEventError(),
    adapter_types.AdapterRegistered(adapter_name="dbt-awesome", adapter_version="1.2.3"),
    adapter_types.NewConnection(conn_type="", conn_name=""),
    adapter_types.ConnectionReused(conn_name=""),
    adapter_types.ConnectionLeftOpenInCleanup(conn_name=""),
    adapter_types.ConnectionClosedInCleanup(conn_name=""),
    adapter_types.RollbackFailed(conn_name=""),
    adapter_types.ConnectionClosed(conn_name=""),
    adapter_types.ConnectionLeftOpen(conn_name=""),
    adapter_types.Rollback(conn_name=""),
    adapter_types.CacheMiss(conn_name="", database="", schema=""),
    adapter_types.ListRelations(database="", schema=""),
    adapter_types.ConnectionUsed(conn_type="", conn_name=""),
    adapter_types.SQLQuery(conn_name="", sql=""),
    adapter_types.SQLQueryStatus(status="", elapsed=0.1),
    adapter_types.SQLCommit(conn_name=""),
    adapter_types.ColTypeChange(
        orig_type="",
        new_type="",
        table={"database": "", "schema": "", "identifier": ""},
    ),
    adapter_types.SchemaCreation(relation={"database": "", "schema": "", "identifier": ""}),
    adapter_types.SchemaDrop(relation={"database": "", "schema": "", "identifier": ""}),
    adapter_types.CacheAction(
        action="adding_relation",
        ref_key={"database": "", "schema": "", "identifier": ""},
        ref_key_2={"database": "", "schema": "", "identifier": ""},
    ),
    adapter_types.CacheDumpGraph(before_after="before", action="rename", dump=dict()),
    adapter_types.AdapterImportError(exc=""),
    adapter_types.PluginLoadError(exc_info=""),
    adapter_types.NewConnectionOpening(connection_state=""),
    adapter_types.CodeExecution(conn_name="", code_content=""),
    adapter_types.CodeExecutionStatus(status="", elapsed=0.1),
    adapter_types.CatalogGenerationError(exc=""),
    adapter_types.WriteCatalogFailure(num_exceptions=0),
    adapter_types.CatalogWritten(path=""),
    adapter_types.CannotGenerateDocs(),
    adapter_types.BuildingCatalog(),
    adapter_types.DatabaseErrorRunningHook(hook_type=""),
    adapter_types.HooksRunning(num_hooks=0, hook_type=""),
    adapter_types.FinishedRunningStats(stat_line="", execution="", execution_time=0),
    adapter_types.ConstraintNotEnforced(constraint="", adapter=""),
    adapter_types.ConstraintNotSupported(constraint="", adapter=""),
    # I - Project parsing ======================
    core_types.InputFileDiffError(category="testing", file_id="my_file"),
    core_types.InvalidValueForField(field_name="test", field_value="test"),
    core_types.ValidationWarning(resource_type="model", field_name="access", node_name="my_macro"),
    core_types.ParsePerfInfoPath(path=""),
    core_types.PartialParsingErrorProcessingFile(file=""),
    core_types.PartialParsingFile(file_id=""),
    core_types.PartialParsingError(exc_info={}),
    core_types.PartialParsingSkipParsing(),
    core_types.UnableToPartialParse(reason="something went wrong"),
    core_types.StateCheckVarsHash(vars="testing", target="testing", profile="testing"),
    core_types.PartialParsingNotEnabled(),
    core_types.ParsedFileLoadFailed(path="", exc="", exc_info=""),
    core_types.PartialParsingEnabled(deleted=0, added=0, changed=0),
    core_types.PartialParsingFile(file_id=""),
    core_types.InvalidDisabledTargetInTestNode(
        resource_type_title="",
        unique_id="",
        original_file_path="",
        target_kind="",
        target_name="",
        target_package="",
    ),
    core_types.UnusedResourceConfigPath(unused_config_paths=[]),
    core_types.SeedIncreased(package_name="", name=""),
    core_types.SeedExceedsLimitSamePath(package_name="", name=""),
    core_types.SeedExceedsLimitAndPathChanged(package_name="", name=""),
    core_types.SeedExceedsLimitChecksumChanged(package_name="", name="", checksum_name=""),
    core_types.UnusedTables(unused_tables=[]),
    core_types.WrongResourceSchemaFile(
        patch_name="", resource_type="", file_path="", plural_resource_type=""
    ),
    core_types.NoNodeForYamlKey(patch_name="", yaml_key="", file_path=""),
    core_types.MacroNotFoundForPatch(patch_name=""),
    core_types.NodeNotFoundOrDisabled(
        original_file_path="",
        unique_id="",
        resource_type_title="",
        target_name="",
        target_kind="",
        target_package="",
        disabled="",
    ),
    core_types.JinjaLogWarning(),
    core_types.JinjaLogInfo(msg=""),
    core_types.JinjaLogDebug(msg=""),
    core_types.UnpinnedRefNewVersionAvailable(
        ref_node_name="", ref_node_package="", ref_node_version="", ref_max_version=""
    ),
    core_types.DeprecatedModel(model_name="", model_version="", deprecation_date=""),
    core_types.DeprecatedReference(
        model_name="",
        ref_model_name="",
        ref_model_package="",
        ref_model_deprecation_date="",
        ref_model_latest_version="",
    ),
    core_types.UpcomingReferenceDeprecation(
        model_name="",
        ref_model_name="",
        ref_model_package="",
        ref_model_deprecation_date="",
        ref_model_latest_version="",
    ),
    core_types.UnsupportedConstraintMaterialization(materialized=""),
    core_types.ParseInlineNodeError(exc=""),
    core_types.SemanticValidationFailure(msg=""),
    core_types.UnversionedBreakingChange(
        breaking_changes=[],
        model_name="",
        model_file_path="",
        contract_enforced_disabled=True,
        columns_removed=[],
        column_type_changes=[],
        enforced_column_constraint_removed=[],
        enforced_model_constraint_removed=[],
        materialization_changed=[],
    ),
    core_types.WarnStateTargetEqual(state_path=""),
    core_types.FreshnessConfigProblem(msg=""),
    core_types.SemanticValidationFailure(msg=""),
    core_types.MicrobatchModelNoEventTimeInputs(model_name=""),
    core_types.InvalidConcurrentBatchesConfig(num_models=1, adapter_type=""),
    core_types.InvalidMacroAnnotation(msg="", macro_file_path="", macro_unique_id=""),
    # M - Deps generation ======================
    core_types.GitSparseCheckoutSubdirectory(subdir=""),
    core_types.GitProgressCheckoutRevision(revision=""),
    core_types.GitProgressUpdatingExistingDependency(dir=""),
    core_types.GitProgressPullingNewDependency(dir=""),
    core_types.GitNothingToDo(sha=""),
    core_types.GitProgressUpdatedCheckoutRange(start_sha="", end_sha=""),
    core_types.GitProgressCheckedOutAt(end_sha=""),
    core_types.RegistryProgressGETRequest(url=""),
    core_types.RegistryProgressGETResponse(url="", resp_code=1234),
    core_types.SelectorReportInvalidSelector(valid_selectors="", spec_method="", raw_spec=""),
    core_types.DepsNoPackagesFound(),
    core_types.DepsStartPackageInstall(package_name=""),
    core_types.DepsInstallInfo(version_name=""),
    core_types.DepsUpdateAvailable(version_latest=""),
    core_types.DepsUpToDate(),
    core_types.DepsListSubdirectory(subdirectory=""),
    core_types.DepsNotifyUpdatesAvailable(packages=["my_pkg", "other_pkg"]),
    types.RetryExternalCall(attempt=0, max=0),
    types.RecordRetryException(exc=""),
    core_types.RegistryIndexProgressGETRequest(url=""),
    core_types.RegistryIndexProgressGETResponse(url="", resp_code=1234),
    core_types.RegistryResponseUnexpectedType(response=""),
    core_types.RegistryResponseMissingTopKeys(response=""),
    core_types.RegistryResponseMissingNestedKeys(response=""),
    core_types.RegistryResponseExtraNestedKeys(response=""),
    core_types.DepsSetDownloadDirectory(path=""),
    core_types.DepsLockUpdating(lock_filepath=""),
    core_types.DepsAddPackage(package_name="", version="", packages_filepath=""),
    core_types.DepsFoundDuplicatePackage(removed_package={}),
    core_types.DepsScrubbedPackageName(package_name=""),
    core_types.DepsUnpinned(revision="", git=""),
    core_types.NoNodesForSelectionCriteria(spec_raw=""),
    # P - Artifacts ======================
    core_types.ArtifactWritten(artifact_type="manifest", artifact_path="path/to/artifact.json"),
    # Q - Node execution ======================
    core_types.RunningOperationCaughtError(exc=""),
    core_types.CompileComplete(),
    core_types.FreshnessCheckComplete(),
    core_types.SeedHeader(header=""),
    core_types.SQLRunnerException(exc=""),
    core_types.LogTestResult(
        name="",
        index=0,
        num_models=0,
        execution_time=0,
        num_failures=0,
    ),
    core_types.LogNodeResult(
        description="",
        status="",
        index=0,
        total=0,
        execution_time=0,
        msg="",
    ),
    core_types.LogStartLine(description="", index=0, total=0),
    core_types.LogModelResult(
        description="",
        status="",
        index=0,
        total=0,
        execution_time=0,
    ),
    core_types.LogSnapshotResult(
        status="",
        description="",
        cfg={},
        index=0,
        total=0,
        execution_time=0,
    ),
    core_types.LogSeedResult(
        status="",
        index=0,
        total=0,
        execution_time=0,
        schema="",
        relation="",
    ),
    core_types.LogFreshnessResult(
        source_name="",
        table_name="",
        index=0,
        total=0,
        execution_time=0,
    ),
    core_types.LogNodeNoOpResult(
        description="",
        status="",
        index=0,
        total=0,
        execution_time=0,
    ),
    core_types.LogCancelLine(conn_name=""),
    core_types.DefaultSelector(name=""),
    core_types.NodeStart(),
    core_types.NodeFinished(),
    core_types.QueryCancelationUnsupported(type=""),
    core_types.ConcurrencyLine(num_threads=0, target_name=""),
    core_types.WritingInjectedSQLForNode(),
    core_types.NodeCompiling(),
    core_types.NodeExecuting(),
    core_types.LogHookStartLine(
        statement="",
        index=0,
        total=0,
    ),
    core_types.LogHookEndLine(
        statement="",
        status="",
        index=0,
        total=0,
        execution_time=0,
    ),
    core_types.SkippingDetails(
        resource_type="",
        schema="",
        node_name="",
        index=0,
        total=0,
    ),
    core_types.NothingToDo(),
    core_types.RunningOperationUncaughtError(exc=""),
    core_types.EndRunResult(),
    core_types.NoNodesSelected(),
    core_types.CommandCompleted(
        command="",
        success=True,
        elapsed=0.1,
        completed_at=get_json_string_utcnow(),
    ),
    core_types.ShowNode(node_name="", preview="", is_inline=True, unique_id="model.test.my_model"),
    core_types.CompiledNode(
        node_name="", compiled="", is_inline=True, unique_id="model.test.my_model"
    ),
    core_types.SnapshotTimestampWarning(
        snapshot_time_data_type="DATETIME", updated_at_data_type="DATETIMEZ"
    ),
    core_types.MicrobatchExecutionDebug(msg=""),
    core_types.LogStartBatch(description="", batch_index=0, total_batches=0),
    core_types.LogBatchResult(
        description="",
        status="",
        batch_index=0,
        total_batches=0,
        execution_time=0,
    ),
    # W - Node testing ======================
    core_types.CatchableExceptionOnRun(exc=""),
    core_types.InternalErrorOnRun(build_path="", exc=""),
    core_types.GenericExceptionOnRun(build_path="", unique_id="", exc=""),
    core_types.NodeConnectionReleaseError(node_name="", exc=""),
    core_types.FoundStats(stat_line=""),
    # Z - misc ======================
    core_types.MainKeyboardInterrupt(),
    core_types.MainEncounteredError(exc=""),
    core_types.MainStackTrace(stack_trace=""),
    types.SystemCouldNotWrite(path="", reason="", exc=""),
    types.SystemExecutingCmd(cmd=[""]),
    types.SystemStdOut(bmsg=str(b"")),
    types.SystemStdErr(bmsg=str(b"")),
    types.SystemReportReturnCode(returncode=0),
    core_types.TimingInfoCollected(),
    core_types.LogDebugStackTrace(),
    core_types.CheckCleanPath(path=""),
    core_types.ConfirmCleanPath(path=""),
    core_types.ProtectedCleanPath(path=""),
    core_types.FinishedCleanPaths(),
    core_types.OpenCommand(open_cmd="", profiles_dir=""),
    core_types.RunResultWarning(resource_type="", node_name="", path=""),
    core_types.RunResultFailure(resource_type="", node_name="", path=""),
    core_types.StatsLine(
        stats={"error": 0, "skip": 0, "pass": 0, "warn": 0, "noop": 0, "total": 0}
    ),
    core_types.RunResultError(msg=""),
    core_types.RunResultErrorNoMessage(status=""),
    core_types.SQLCompiledPath(path=""),
    core_types.CheckNodeTestFailure(relation_name=""),
    core_types.EndOfRunSummary(num_errors=0, num_warnings=0, keyboard_interrupt=False),
    core_types.MarkSkippedChildren(unique_id="", status="skipped"),
    core_types.LogSkipBecauseError(schema="", relation="", index=0, total=0),
    core_types.EnsureGitInstalled(),
    core_types.DepsCreatingLocalSymlink(),
    core_types.DepsSymlinkNotAvailable(),
    core_types.DisableTracking(),
    core_types.SendingEvent(kwargs=""),
    core_types.SendEventFailure(),
    core_types.FlushEvents(),
    core_types.FlushEventsFailure(),
    types.Formatting(),
    core_types.TrackingInitializeFailure(),
    core_types.RunResultWarningMessage(),
    core_types.DebugCmdOut(),
    core_types.DebugCmdResult(),
    core_types.ListCmdOut(),
    types.Note(msg="This is a note."),
    core_types.ResourceReport(),
    core_types.ArtifactUploadSuccess(),
    core_types.ArtifactUploadError(),
    core_types.ArtifactUploadSkipped(),
]


class TestEventJSONSerialization:

    # attempts to test that every event is serializable to json.
    # event types that take `Any` are not possible to test in this way since some will serialize
    # just fine and others won't.
    def test_all_serializable(self):
        all_non_abstract_events = set(
            get_all_subclasses(CoreBaseEvent),
        )
        all_event_values_list = list(map(lambda x: x.__class__, sample_values))
        diff = all_non_abstract_events.difference(set(all_event_values_list))
        assert (
            not diff
        ), f"{diff}test is missing concrete values in `sample_values`. Please add the values for the aforementioned event classes"

        # make sure everything in the list is a value not a type
        for event in sample_values:
            assert type(event) != type

        # if we have everything we need to test, try to serialize everything
        count = 0
        for event in sample_values:
            msg = msg_from_base_event(event)
            print(f"--- msg: {msg.info.name}")
            # Serialize to dictionary
            try:
                msg_to_dict(msg)
            except Exception as e:
                raise Exception(
                    f"{event} can not be converted to a dict. Originating exception: {e}"
                )
            # Serialize to json
            try:
                msg_to_json(msg)
            except Exception as e:
                raise Exception(f"{event} is not serializable to json. Originating exception: {e}")
            # Serialize to binary
            try:
                msg.SerializeToString()
            except Exception as e:
                raise Exception(
                    f"{event} is not serializable to binary protobuf. Originating exception: {e}"
                )
            count += 1
        print(f"--- Found {count} events")


T = TypeVar("T")


def test_date_serialization():
    ti = TimingInfo("compile")
    ti.begin()
    ti.end()
    ti_dict = ti.to_dict()
    assert ti_dict["started_at"].endswith("Z")
    assert ti_dict["completed_at"].endswith("Z")


def test_bad_serialization():
    """Tests that bad serialization enters the proper exception handling

    When pytest is in use the exception handling of `BaseEvent` raises an
    exception. When pytest isn't present, it fires a Note event. Thus to test
    that bad serializations are properly handled, the best we can do is test
    that the exception handling path is used.
    """

    with pytest.raises(Exception) as excinfo:
        types.Note(param_event_doesnt_have="This should break")

    assert 'has no field named "param_event_doesnt_have" at "Note"' in str(excinfo.value)


def test_single_run_error():

    try:
        # Add a recording event manager to the context, so we can test events.
        event_mgr = TestEventManager()
        ctx_set_event_manager(event_mgr)

        class MockNode:
            unique_id: str = ""
            node_info = None
            resource_type: str = "model"
            name: str = "my_model"
            original_file_path: str = "path/to/model.sql"

        error_result = RunResult(
            status=RunStatus.Error,
            timing=[],
            thread_id="",
            execution_time=0.0,
            node=MockNode(),
            adapter_response=dict(),
            message="oh no!",
            failures=1,
            batch_results=None,
        )
        results = [error_result]
        print_run_end_messages(results)

        summary_event = [
            e for e in event_mgr.event_history if isinstance(e[0], core_types.EndOfRunSummary)
        ]
        run_result_error_events = [
            e for e in event_mgr.event_history if isinstance(e[0], core_types.RunResultError)
        ]

        # expect correct plural
        assert "partial successes" in summary_event[0][0].message()

        # expect one error to show up
        assert len(run_result_error_events) == 1
        assert run_result_error_events[0][0].msg == "oh no!"

    finally:
        # Set an empty event manager unconditionally on exit. This is an early
        # attempt at unit testing events, and we need to think about how it
        # could be done in a thread safe way in the long run.
        ctx_set_event_manager(EventManager())
