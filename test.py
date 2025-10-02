#!/usr/bin/env python3
"""
QuixStreams Samples - Python Test Runner

A parallel test runner for docker-compose based integration tests.
Supports parallel execution, automatic retry of failures, and detailed reporting.

Usage:
    ./test.py test <app-path> [...]  # Test specific apps
    ./test.py test-all               # Run all tests
    ./test.py test-sources -p 3      # Run all source tests in parallel
    ./test.py --help                 # Show full help
"""

import asyncio
import signal
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
import subprocess
import json
import time


# ============================================================================
# Configuration Constants
# ============================================================================

# Status update timing
STATUS_CHECK_INTERVAL = 20  # Check running tests every N seconds
LONG_RUNNING_THRESHOLD = 35  # Only show status if any test > N seconds

# Default timeouts
DEFAULT_TEST_TIMEOUT = 300  # 5 minutes


# ============================================================================
# Data Models
# ============================================================================

class TestStatus(Enum):
    """Test execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """Result of a single test execution"""
    name: str  # e.g., "sources/starter_source"
    status: TestStatus
    duration: int  # seconds
    error_message: Optional[str] = None
    was_retried: bool = False


@dataclass
class TestReport:
    """Summary report of all test executions"""
    total: int
    passed: int
    failed: int
    skipped: int
    results: List[TestResult]
    total_duration: int
    parallel_duration: int = 0
    retry_duration: int = 0

    @property
    def passed_first_try(self) -> List[TestResult]:
        """Tests that passed on first attempt"""
        return [r for r in self.results if r.status == TestStatus.PASSED and not r.was_retried]

    @property
    def passed_after_retry(self) -> List[TestResult]:
        """Tests that passed after retry"""
        return [r for r in self.results if r.status == TestStatus.PASSED and r.was_retried]

    @property
    def failed_tests(self) -> List[TestResult]:
        """Tests that failed (even after retry)"""
        return [r for r in self.results if r.status == TestStatus.FAILED]

    @property
    def skipped_tests(self) -> List[TestResult]:
        """Tests that were skipped"""
        return [r for r in self.results if r.status == TestStatus.SKIPPED]


# ============================================================================
# Test Discovery
# ============================================================================

class TestDiscovery:
    """
    Discovers available tests in the test directory.

    Tests are identified by the presence of docker-compose.test.yml files
    in subdirectories under tests/{sources,destinations,transformations}.
    """

    def __init__(self, tests_dir: Path):
        self.tests_dir = tests_dir
        self.config_file = tests_dir.parent / "test-config.json"
        self.excluded_apps = self._load_exclusions()
        self.script_dir = tests_dir.parent

    def _load_exclusions(self) -> Dict[str, str]:
        """Load excluded apps from test-config.json"""
        if not self.config_file.exists():
            return {}

        try:
            with open(self.config_file) as f:
                config = json.load(f)
                return config.get("excluded_from_testing", {})
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def find_all_tests(self) -> List[Path]:
        """Find all test directories with docker-compose.test.yml"""
        tests = []

        for category in ["sources", "destinations", "transformations"]:
            tests.extend(self.find_tests_by_pattern(category))

        return sorted(tests)

    def find_tests_by_pattern(self, pattern: str) -> List[Path]:
        """Find tests matching pattern (sources, destinations, transformations)"""
        tests = []
        category_dir = self.tests_dir / pattern

        if not category_dir.exists():
            return tests

        for test_dir in category_dir.iterdir():
            if test_dir.is_dir():
                compose_file = test_dir / "docker-compose.test.yml"
                if compose_file.exists():
                    tests.append(test_dir)

        return sorted(tests)

    def is_excluded(self, test_name: str) -> Optional[str]:
        """Check if test is excluded, return reason if so"""
        # test_name could be "sources/starter_source" or just "starter_source"
        # Check both formats
        app_name = test_name.split("/")[-1]  # Get just the app name

        return self.excluded_apps.get(app_name) or self.excluded_apps.get(test_name)

    def find_untested_apps(self) -> Dict[str, List[str]]:
        """Find applications that don't have tests"""
        untested = {"sources": [], "destinations": [], "transformations": []}

        python_dir = self.script_dir / "python"

        for category in ["sources", "destinations", "transformations"]:
            category_dir = python_dir / category

            if not category_dir.exists():
                continue

            for app_dir in category_dir.iterdir():
                if app_dir.is_dir():
                    app_name = app_dir.name
                    test_dir = self.tests_dir / category / app_name

                    # Skip if excluded
                    if self.is_excluded(app_name):
                        continue

                    # Check if test exists
                    if not (test_dir / "docker-compose.test.yml").exists():
                        untested[category].append(app_name)

        return untested


# ============================================================================
# Test Execution
# ============================================================================

class TestExecutor:
    """Executes individual tests using docker compose"""

    def __init__(self, verbose: bool = False, default_timeout: int = DEFAULT_TEST_TIMEOUT):
        self.verbose = verbose
        self.default_timeout = default_timeout
        self.script_dir = Path(__file__).parent

    def run_test(self, test_path: Path) -> TestResult:
        """
        Run a single test synchronously

        Maps to bash: run_single_test()
        """
        test_name = str(test_path.relative_to(self.script_dir / "tests"))
        compose_file = test_path / "docker-compose.test.yml"

        # Check if docker-compose.test.yml exists
        if not compose_file.exists():
            if not self.verbose:
                ReportFormatter.print_error(f"{test_name}: FAILED (0s) - No docker-compose.test.yml found")
            return TestResult(
                name=test_name,
                status=TestStatus.FAILED,
                duration=0,
                error_message="No docker-compose.test.yml found"
            )

        # Print header (only in non-parallel mode)
        if self.verbose:
            ReportFormatter.print_header(f"Testing: {test_name}")

        # Change to test directory
        original_dir = Path.cwd()

        try:
            test_path.resolve()  # Ensure path is absolute

            # Run setup.sh if it exists
            setup_script = test_path / "setup.sh"
            if setup_script.exists():
                if self.verbose:
                    ReportFormatter.print_info("Running setup script...")

                result = subprocess.run(
                    ["bash", "setup.sh"],
                    cwd=test_path,
                    capture_output=not self.verbose,
                    text=True
                )

                if result.returncode != 0:
                    if not self.verbose:
                        ReportFormatter.print_error(f"{test_name}: FAILED (0s) - Setup script failed")
                    else:
                        ReportFormatter.print_error(f"Setup script failed with exit code {result.returncode}")
                    return TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        duration=0,
                        error_message="Setup script failed"
                    )

            # Start timing
            start_time = time.time()

            # Run docker compose test
            stdout_mode = None if self.verbose else subprocess.DEVNULL
            process = None

            # Check for per-test timeout in docker-compose.test.yml
            # Look for: # timeout: 600
            test_timeout = self.default_timeout
            try:
                with open(compose_file) as f:
                    first_lines = [f.readline() for _ in range(5)]  # Check first 5 lines
                    for line in first_lines:
                        line = line.strip()
                        if line.startswith('# timeout:') or line.startswith('#timeout:'):
                            timeout_str = line.split(':', 1)[1].strip()
                            test_timeout = int(timeout_str)
                            if self.verbose:
                                ReportFormatter.print_info(f"Using test-specific timeout: {test_timeout}s")
                            break
            except (ValueError, OSError, IndexError):
                pass  # Use default if parsing fails or no timeout specified

            try:
                # Use docker compose --timeout flag for graceful shutdown
                # and subprocess timeout as a hard limit
                process = subprocess.Popen(
                    ["docker", "compose", "-f", "docker-compose.test.yml",
                     "up", "--build", "--abort-on-container-exit",
                     "--timeout", str(min(10, test_timeout // 10))],  # Graceful shutdown timeout
                    cwd=test_path,
                    stdout=stdout_mode,
                    stderr=subprocess.STDOUT
                )

                try:
                    result_code = process.wait(timeout=test_timeout)
                    result = type('obj', (object,), {'returncode': result_code})()
                except subprocess.TimeoutExpired:
                    # Test timed out
                    process.kill()
                    process.wait()
                    if not self.verbose:
                        ReportFormatter.print_error(f"{test_name}: FAILED ({test_timeout}s) - Timed out")
                    return TestResult(
                        name=test_name,
                        status=TestStatus.FAILED,
                        duration=test_timeout,
                        error_message=f"Test timed out after {test_timeout}s"
                    )

                # Calculate duration
                duration = int(time.time() - start_time)
            except KeyboardInterrupt:
                # User interrupted, kill the process
                if process:
                    process.terminate()
                    try:
                        process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        process.kill()
                raise
            finally:
                # Always cleanup docker containers
                subprocess.run(
                    ["docker", "compose", "-f", "docker-compose.test.yml", "down", "-v"],
                    cwd=test_path,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )

            # Determine status
            if result.returncode == 0:
                status = TestStatus.PASSED
                error_message = None
                if not self.verbose:
                    ReportFormatter.print_success(f"{test_name}: PASSED ({duration}s)")
            else:
                status = TestStatus.FAILED
                error_message = "Test execution failed"
                if not self.verbose:
                    ReportFormatter.print_error(f"{test_name}: FAILED ({duration}s)")

            return TestResult(
                name=test_name,
                status=status,
                duration=duration,
                error_message=error_message
            )

        finally:
            # Always return to original directory
            pass  # We never changed directory, so nothing to restore

    async def run_test_async(self, test_path: Path) -> TestResult:
        """
        Run a single test asynchronously (for parallel execution)

        Uses asyncio to run in thread pool
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run_test, test_path)


# ============================================================================
# Parallel Test Runner
# ============================================================================

class ParallelTestRunner:
    """
    Runs tests in parallel with automatic retry

    Maps to bash: run_multiple_tests_parallel() and run_all_parallel()
    """

    def __init__(self, max_parallel: int = 3, enable_retry: bool = True, timeout: int = DEFAULT_TEST_TIMEOUT, verbose: bool = False):
        self.max_parallel = max_parallel
        self.enable_retry = enable_retry
        self.timeout = timeout
        self.executor = TestExecutor(verbose=verbose, default_timeout=timeout)
        self.discovery = TestDiscovery(Path(__file__).parent / "tests")

    async def run_tests(self, test_paths: List[Path]) -> TestReport:
        """
        Run multiple tests in parallel with retry logic

        Flow:
        1. Run all tests in parallel (up to max_parallel concurrent)
        2. Collect failures
        3. Retry failures sequentially
        4. Generate final report
        """
        overall_start = time.time()

        # Print header
        ReportFormatter.print_header(
            f"Running {len(test_paths)} tests (parallel mode, max {self.max_parallel} concurrent)"
        )
        print()

        # Phase 1: Parallel execution
        parallel_start = time.time()
        results = await self._run_parallel_phase(test_paths)
        parallel_duration = int(time.time() - parallel_start)

        # Phase 2: Retry failures
        retry_duration = 0
        if self.enable_retry:
            failed_results = [r for r in results if r.status == TestStatus.FAILED]

            if failed_results:
                print()
                ReportFormatter.print_header("Retrying Failed Tests Sequentially")
                ReportFormatter.print_info(f"Retrying {len(failed_results)} tests that may have failed due to resource contention...")
                print()

                retry_start = time.time()
                retried_results = await self._retry_failures(failed_results)
                retry_duration = int(time.time() - retry_start)

                # Update results list with retry outcomes
                for retry_result in retried_results:
                    for i, orig_result in enumerate(results):
                        if orig_result.name == retry_result.name:
                            results[i] = retry_result
                            break

        total_duration = int(time.time() - overall_start)

        # Build report
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)

        return TestReport(
            total=len(results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            results=results,
            total_duration=total_duration,
            parallel_duration=parallel_duration,
            retry_duration=retry_duration
        )

    async def _run_parallel_phase(self, test_paths: List[Path]) -> List[TestResult]:
        """Run tests in parallel using asyncio.Semaphore"""
        semaphore = asyncio.Semaphore(self.max_parallel)
        results = []
        total = len(test_paths)

        # Track running tests for status updates
        running_tests = {}  # {test_name: start_time}

        async def run_with_semaphore(idx: int, test_path: Path) -> TestResult:
            test_name = str(test_path.relative_to(Path(__file__).parent / "tests"))

            # Check if excluded
            exclusion_reason = self.discovery.is_excluded(test_name)
            if exclusion_reason:
                ReportFormatter.print_info(f"[{idx+1}/{total}] {test_name}: SKIPPED - {exclusion_reason}")
                return TestResult(
                    name=test_name,
                    status=TestStatus.SKIPPED,
                    duration=0,
                    error_message=exclusion_reason
                )

            async with semaphore:
                ReportFormatter.print_info(f"Starting [{idx+1}/{total}]: {test_name}")
                running_tests[test_name] = time.time()
                result = await self.executor.run_test_async(test_path)
                if test_name in running_tests:
                    del running_tests[test_name]
                return result

        # Launch all tests
        tasks = {asyncio.create_task(run_with_semaphore(i, path)):
                 str(path.relative_to(Path(__file__).parent / "tests"))
                 for i, path in enumerate(test_paths)}

        # Wait for completion with periodic status updates
        ReportFormatter.print_info("Waiting for all tests to complete...")
        print()

        pending = set(tasks.keys())
        completed_results = []
        last_status_time = time.time()

        while pending:
            # Wait up to 20 seconds for tasks to complete
            done, pending = await asyncio.wait(pending, timeout=20)

            # Collect results from completed tasks
            for task in done:
                completed_results.append(await task)

            # Print status update if there are still tests running and any has been running for longer than threshold
            if pending and time.time() - last_status_time >= STATUS_CHECK_INTERVAL:
                current_time = time.time()
                # Check if any test has been running > threshold
                has_long_running = any(current_time - start > LONG_RUNNING_THRESHOLD for start in running_tests.values())

                if has_long_running:
                    print()
                    num_running = len(running_tests)
                    ReportFormatter.print_info(f"Still running ({num_running} test{'s' if num_running != 1 else ''}):")
                    # Sort by elapsed time (longest running first)
                    sorted_tests = sorted(running_tests.items(), key=lambda x: x[1])
                    for test_name, start_time in sorted_tests:
                        elapsed = int(current_time - start_time)
                        print(f"  - {test_name} ({elapsed}s)")
                    print()
                last_status_time = current_time

        return completed_results

    async def _retry_failures(self, failed_results: List[TestResult]) -> List[TestResult]:
        """Retry failed tests sequentially"""
        retried_results = []

        for failed in failed_results:
            ReportFormatter.print_info(f"Retrying: {failed.name}")

            # Find the test path
            test_path = Path(__file__).parent / "tests" / failed.name

            # Run retry with non-verbose mode (same as first run)
            result = self.executor.run_test(test_path)

            # Mark as retried if it passed
            if result.status == TestStatus.PASSED:
                result.was_retried = True

            retried_results.append(result)

        return retried_results


# ============================================================================
# Sequential Test Runner (for comparison/fallback)
# ============================================================================

class SequentialTestRunner:
    """
    Runs tests sequentially (one at a time)

    Maps to bash: run_multiple_tests_sequential()
    """

    def __init__(self, timeout: int = DEFAULT_TEST_TIMEOUT, verbose: bool = False):
        self.timeout = timeout
        self.executor = TestExecutor(verbose=verbose, default_timeout=timeout)
        self.discovery = TestDiscovery(Path(__file__).parent / "tests")

    def run_tests(self, test_paths: List[Path]) -> TestReport:
        """Run tests one by one"""
        results = []
        start_time = time.time()

        # Print header
        ReportFormatter.print_header(
            f"Running {len(test_paths)} tests (serial mode)"
        )
        print()

        for idx, test_path in enumerate(test_paths):
            test_name = str(test_path.relative_to(Path(__file__).parent / "tests"))

            # Check if excluded
            exclusion_reason = self.discovery.is_excluded(test_name)
            if exclusion_reason:
                ReportFormatter.print_info(f"[{idx+1}/{len(test_paths)}] {test_name}: SKIPPED - {exclusion_reason}")
                results.append(TestResult(
                    name=test_name,
                    status=TestStatus.SKIPPED,
                    duration=0,
                    error_message=exclusion_reason
                ))
                continue

            # Print starting message
            ReportFormatter.print_info(f"Starting [{idx+1}/{len(test_paths)}]: {test_name}")

            # Run test
            result = self.executor.run_test(test_path)
            results.append(result)

        total_duration = int(time.time() - start_time)

        # Build report
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)

        return TestReport(
            total=len(results),
            passed=passed,
            failed=failed,
            skipped=skipped,
            results=results,
            total_duration=total_duration
        )


# ============================================================================
# Output Formatting
# ============================================================================

class Colors:
    """ANSI color codes"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[1;36m'
    NC = '\033[0m'  # No Color


class ReportFormatter:
    """
    Formats test reports for terminal output

    Maps to bash: print_header(), print_success(), etc.
    """

    @staticmethod
    def print_header(text: str):
        """Print a section header"""
        print(f"{Colors.BLUE}{'=' * 32}{Colors.NC}")
        print(f"{Colors.BLUE}{text}{Colors.NC}")
        print(f"{Colors.BLUE}{'=' * 32}{Colors.NC}")

    @staticmethod
    def print_success(text: str):
        """Print success message"""
        print(f"{Colors.GREEN}{text}{Colors.NC}")

    @staticmethod
    def print_error(text: str):
        """Print error message"""
        print(f"{Colors.RED}{text}{Colors.NC}")

    @staticmethod
    def print_info(text: str):
        """Print info message"""
        print(f"{Colors.YELLOW}{text}{Colors.NC}")

    @staticmethod
    def format_retry_results(passed: List[TestResult], failed: List[TestResult]):
        """Format retry results section"""
        # TODO: Implement
        # Show which tests passed on retry with duration
        # Show which tests still failed
        pass

    @staticmethod
    def format_final_summary(report: TestReport, parallel_count: int = None):
        """
        Format final test summary

        Maps to bash final summary section
        Shows:
        - Total tests
        - Passed on first try (with durations)
        - Passed after retry (with durations)
        - Failed
        - Skipped
        - Duration breakdown
        - Speedup calculation
        """
        ReportFormatter.print_header("Final Test Summary")
        print(f"Total:   {report.total}")
        print()

        # Passed on first try
        first_try_passed = report.passed_first_try
        print(f"{Colors.GREEN}Passed on first try:  {len(first_try_passed)}{Colors.NC}")
        if first_try_passed:
            for result in first_try_passed:
                print(f"  - {result.name} ({result.duration}s)")
        print()

        # Passed after retry
        retry_passed = report.passed_after_retry
        if retry_passed:
            print(f"{Colors.GREEN}Passed after retry:   {len(retry_passed)}{Colors.NC}")
            for result in retry_passed:
                print(f"  - {result.name} ({result.duration}s on retry)")
            print()

        # Failed
        failed_tests = report.failed_tests
        print(f"{Colors.RED}Failed:  {report.failed}{Colors.NC}")
        if failed_tests:
            for result in failed_tests:
                print(f"  - {result.name}")
            print()

            # Show command to re-run failed tests
            if len(failed_tests) > 0:
                failed_names = " ".join(r.name for r in failed_tests)
                print(f"{Colors.YELLOW}Re-run failed tests:{Colors.NC}")
                print(f"  ./test.py test {failed_names}")
        print()

        # Skipped
        skipped_tests = report.skipped_tests
        if report.skipped > 0:
            print(f"{Colors.YELLOW}Skipped: {report.skipped}{Colors.NC}")
            if skipped_tests:
                for result in skipped_tests:
                    print(f"  - {result.name}")
            print()

        # Duration
        if parallel_count is not None:
            print(f"{Colors.BLUE}Total Duration: {report.total_duration}s (parallelism: {parallel_count}){Colors.NC}")
        else:
            print(f"{Colors.BLUE}Total Duration: {report.total_duration}s{Colors.NC}")

        if report.retry_duration > 0:
            print(f"{Colors.BLUE}Parallel phase: {report.parallel_duration}s{Colors.NC}")
            print(f"{Colors.BLUE}Retry phase:    {report.retry_duration}s{Colors.NC}")

        # Calculate speedup for parallel mode
        if parallel_count is not None and report.total_duration > 0:
            # Estimate sequential time (sum of all test durations)
            estimated_sequential = sum(r.duration for r in report.results)
            if estimated_sequential > 0:
                speedup = estimated_sequential / report.total_duration
                print(f"{Colors.BLUE}Speedup:        {speedup:.1f}x{Colors.NC}")
        print()


# ============================================================================
# CLI Interface
# ============================================================================

class TestCLI:
    """
    Command-line interface for test runner

    Maps to bash case statement in test.sh
    Commands: test, test-all, test-sources, test-destinations, etc.
    """

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.discovery = TestDiscovery(self.script_dir / "tests")
        self.parallel_count = None  # None = sequential, number = parallel with count
        self.timeout = DEFAULT_TEST_TIMEOUT
        self.verbose = False  # Default to non-verbose
        self.repeat_count = 1  # Default to run once

    def run(self, args: List[str]):
        """Main entry point"""
        if len(args) == 0 or args[0] in ["help", "--help", "-h"]:
            self.show_help()
            return

        command = args[0]
        remaining_args = args[1:]

        # Parse flags that come after the command
        remaining_args = self._parse_flags(remaining_args)

        if command == "test":
            if len(remaining_args) < 1:
                ReportFormatter.print_error("Usage: ./test.py test <app-path> [<app-path> ...] [-p N]")
                sys.exit(1)
            self.run_tests(remaining_args)

        elif command == "test-all":
            self.run_all()

        elif command == "test-sources":
            self.run_category("sources")

        elif command == "test-destinations":
            self.run_category("destinations")

        elif command == "test-transformations":
            self.run_category("transformations")

        elif command == "list":
            self.list_tests()

        elif command == "list-untested":
            self.list_untested()

        else:
            ReportFormatter.print_error(f"Unknown command: {command}")
            self.show_help()
            sys.exit(1)

    def _parse_flags(self, args: List[str]) -> List[str]:
        """Parse and remove flags from args, return remaining args"""
        remaining = []
        i = 0
        while i < len(args):
            arg = args[i]
            if arg in ["-p", "--parallel"]:
                # Next arg should be the number
                if i + 1 < len(args):
                    try:
                        self.parallel_count = int(args[i + 1])
                        i += 2  # Skip both flag and value
                        continue
                    except ValueError:
                        ReportFormatter.print_error(f"Invalid parallel count: {args[i + 1]}")
                        sys.exit(1)
                else:
                    ReportFormatter.print_error("--parallel requires a number")
                    sys.exit(1)
            elif arg.startswith("--parallel="):
                # --parallel=3 format
                try:
                    self.parallel_count = int(arg.split("=")[1])
                    i += 1
                    continue
                except (ValueError, IndexError):
                    ReportFormatter.print_error(f"Invalid parallel count: {arg}")
                    sys.exit(1)
            elif arg in ["-t", "--timeout"]:
                # Next arg should be timeout in seconds
                if i + 1 < len(args):
                    try:
                        self.timeout = int(args[i + 1])
                        i += 2
                        continue
                    except ValueError:
                        ReportFormatter.print_error(f"Invalid timeout: {args[i + 1]}")
                        sys.exit(1)
                else:
                    ReportFormatter.print_error("--timeout requires a number")
                    sys.exit(1)
            elif arg.startswith("--timeout="):
                # --timeout=600 format
                try:
                    self.timeout = int(arg.split("=")[1])
                    i += 1
                    continue
                except (ValueError, IndexError):
                    ReportFormatter.print_error(f"Invalid timeout: {arg}")
                    sys.exit(1)
            elif arg in ["-v", "--verbose"]:
                # Enable verbose mode (show docker logs)
                self.verbose = True
                i += 1
                continue
            elif arg in ["-r", "--repeat"]:
                # Next arg should be the repeat count
                if i + 1 < len(args):
                    try:
                        self.repeat_count = int(args[i + 1])
                        if self.repeat_count < 1:
                            ReportFormatter.print_error("Repeat count must be at least 1")
                            sys.exit(1)
                        i += 2
                        continue
                    except ValueError:
                        ReportFormatter.print_error(f"Invalid repeat count: {args[i + 1]}")
                        sys.exit(1)
                else:
                    ReportFormatter.print_error("--repeat requires a number")
                    sys.exit(1)
            elif arg.startswith("--repeat="):
                # --repeat=10 format
                try:
                    self.repeat_count = int(arg.split("=")[1])
                    if self.repeat_count < 1:
                        ReportFormatter.print_error("Repeat count must be at least 1")
                        sys.exit(1)
                    i += 1
                    continue
                except (ValueError, IndexError):
                    ReportFormatter.print_error(f"Invalid repeat count: {arg}")
                    sys.exit(1)
            else:
                remaining.append(arg)
                i += 1
        return remaining

    def run_tests(self, test_paths: List[str]):
        """Run one or more tests"""
        # Convert to full paths and validate
        full_paths = []
        for test_path in test_paths:
            full_path = self.script_dir / "tests" / test_path
            if not full_path.exists():
                ReportFormatter.print_error(f"Test not found: {test_path}")
                sys.exit(1)
            full_paths.append(full_path)

        # If only one test and no repeat, run directly with executor for simplicity
        if len(full_paths) == 1 and self.repeat_count == 1:
            executor = TestExecutor(verbose=self.verbose, default_timeout=self.timeout)
            result = executor.run_test(full_paths[0])
            if result.status == TestStatus.FAILED:
                sys.exit(1)
        else:
            # Multiple tests or repeat mode - use the regular test runner
            self._run_tests(full_paths)

    def run_all(self):
        """Run all tests"""
        test_paths = self.discovery.find_all_tests()

        if not test_paths:
            ReportFormatter.print_info("No tests found")
            return

        self._run_tests(test_paths)

    def run_category(self, category: str):
        """Run tests for a category (sources/destinations/transformations)"""
        test_paths = self.discovery.find_tests_by_pattern(category)

        if not test_paths:
            ReportFormatter.print_info(f"No {category} tests found")
            return

        self._run_tests(test_paths)

    def _run_tests(self, test_paths: List[Path]):
        """Run multiple tests (parallel or sequential based on flags)"""
        all_reports = []

        for iteration in range(self.repeat_count):
            if self.repeat_count > 1:
                print()
                ReportFormatter.print_header(f"Iteration {iteration + 1}/{self.repeat_count}")
                print()

            if self.parallel_count is not None:
                runner = ParallelTestRunner(max_parallel=self.parallel_count, timeout=self.timeout, verbose=self.verbose)
                report = asyncio.run(runner.run_tests(test_paths))
            else:
                runner = SequentialTestRunner(timeout=self.timeout, verbose=self.verbose)
                report = runner.run_tests(test_paths)

            all_reports.append(report)

            # Display summary for this iteration
            if self.repeat_count > 1:
                ReportFormatter.format_final_summary(report, parallel_count=self.parallel_count)

        # Display final summary (or only summary if repeat_count == 1)
        if self.repeat_count == 1:
            ReportFormatter.format_final_summary(all_reports[0], parallel_count=self.parallel_count)
        else:
            # Show aggregate summary across all iterations
            print()
            ReportFormatter.print_header(f"Aggregate Summary (all {self.repeat_count} iterations)")

            # Collect statistics per test
            test_stats = {}  # {test_name: {'passed': count, 'failed': count, 'durations': [...]}}

            for report in all_reports:
                for result in report.results:
                    if result.name not in test_stats:
                        test_stats[result.name] = {'passed': 0, 'failed': 0, 'durations': []}

                    if result.status == TestStatus.PASSED:
                        test_stats[result.name]['passed'] += 1
                        test_stats[result.name]['durations'].append(result.duration)
                    elif result.status == TestStatus.FAILED:
                        test_stats[result.name]['failed'] += 1

            # Display per-test statistics
            print()
            for test_name in sorted(test_stats.keys()):
                stats = test_stats[test_name]
                passed = stats['passed']
                failed = stats['failed']
                durations = stats['durations']

                if durations:
                    min_time = min(durations)
                    max_time = max(durations)
                    avg_time = sum(durations) / len(durations)

                    if failed == 0:
                        print(f"{Colors.GREEN}{test_name}: {passed}/{self.repeat_count} passed{Colors.NC}")
                    else:
                        print(f"{Colors.YELLOW}{test_name}: {passed}/{self.repeat_count} passed, {failed} failed{Colors.NC}")

                    print(f"  Duration: min={min_time}s, max={max_time}s, avg={avg_time:.1f}s")
                else:
                    # All failed
                    print(f"{Colors.RED}{test_name}: {failed}/{self.repeat_count} failed{Colors.NC}")

            print()
            total_failed = sum(r.failed for r in all_reports)
            total_passed = sum(r.passed for r in all_reports)
            print(f"Total runs: {len(all_reports) * len(test_paths)}")
            print(f"{Colors.GREEN}Total passed: {total_passed}{Colors.NC}")
            print(f"{Colors.RED}Total failed: {total_failed}{Colors.NC}")

        # Exit with error if any tests failed in any iteration
        if any(r.failed > 0 for r in all_reports):
            sys.exit(1)

    def list_tests(self):
        """List available tests"""
        ReportFormatter.print_header("Available Tests")
        print()

        for category in ["sources", "destinations", "transformations"]:
            tests = self.discovery.find_tests_by_pattern(category)
            if tests:
                print(f"{category.capitalize()}:")
                for test_path in tests:
                    app_name = test_path.name
                    print(f"  - {app_name}")
                print()

    def list_untested(self):
        """List applications without tests"""
        ReportFormatter.print_header("Applications Without Tests")
        print()

        untested = self.discovery.find_untested_apps()
        total_untested = 0

        for category in ["sources", "destinations", "transformations"]:
            apps = untested[category]
            if apps:
                print(f"{category.capitalize()}:")
                for app in apps:
                    print(f"  - {app}")
                    total_untested += 1
                print()

        print()
        ReportFormatter.print_header("Summary")
        print(f"Total applications without tests: {total_untested}")

        if self.discovery.excluded_apps:
            excluded_list = ", ".join(self.discovery.excluded_apps.keys())
            print(f"Excluded from testing: {excluded_list}")

    def show_help(self):
        """Show help text"""
        help_text = """
QuixStreams Samples - Python Test Runner

USAGE:
    ./test.py <command> [options]

COMMANDS:
    test <app-path> [...]     Test one or more specific apps
    test-sources              Test all sources
    test-destinations         Test all destinations
    test-transformations      Test all transformations
    test-all                  Run all tests
    list                      List available tests
    list-untested             List apps without tests
    help                      Show this help

OPTIONS:
    -p, --parallel <N>        Run tests in parallel with N concurrent workers
                              (default is sequential, safe range: 2-4)
    -t, --timeout <seconds>   Maximum time per test (default: 300s / 5min)
                              Per-test: add "# timeout: 600" to docker-compose.test.yml
    -v, --verbose             Show docker logs during test execution (default: hidden)
    -r, --repeat <N>          Run the test suite N times (default: 1)

EXAMPLES:
    ./test.py test sources/simple_csv
    ./test.py test sources/starter_source sources/demo_data -p 2
    ./test.py test sources/failing_source -v
    ./test.py test sources/MQTT --repeat 10
    ./test.py test-all
    ./test.py test-all --parallel 3 --timeout 600
    ./test.py test-sources -p 4 -t 180 --verbose --repeat 5

For detailed documentation, see tests/README.md
"""
        print(help_text)


# ============================================================================
# Main Entry Point
# ============================================================================

def signal_handler(signum, frame):
    """Handle Ctrl-C gracefully"""
    print("\n\nInterrupted! Cleaning up...")
    sys.exit(130)  # Standard exit code for SIGINT


def main():
    """Main entry point"""
    # Register signal handler for Ctrl-C
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    cli = TestCLI()
    cli.run(sys.argv[1:])


if __name__ == "__main__":
    main()
