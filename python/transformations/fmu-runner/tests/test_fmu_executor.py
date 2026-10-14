"""
Unit tests for FMU Executor - Written BEFORE implementation (TDD)

These tests define the expected behavior of the FMU executor module.
"""
import pytest
import numpy as np
import os


class TestShouldProcess:
    """Tests for file extension filtering."""

    def test_should_process_fmu_file(self):
        from fmu_executor import should_process
        assert should_process("model.fmu") == True

    def test_should_not_process_whl_file(self):
        from fmu_executor import should_process
        assert should_process("model.whl") == False

    def test_should_not_process_slx_file(self):
        from fmu_executor import should_process
        assert should_process("model.slx") == False

    def test_should_handle_uppercase_extension(self):
        from fmu_executor import should_process
        assert should_process("model.FMU") == True

    def test_should_handle_empty_filename(self):
        from fmu_executor import should_process
        assert should_process("") == False
        assert should_process(None) == False


class TestReadFmuMetadata:
    """Tests for reading FMU model description."""

    def test_read_bouncing_ball_metadata(self, bouncing_ball_fmu):
        from fmu_executor import read_fmu_metadata

        metadata = read_fmu_metadata(bouncing_ball_fmu)

        assert "inputs" in metadata
        assert "outputs" in metadata
        assert "parameters" in metadata
        assert isinstance(metadata["inputs"], list)
        assert isinstance(metadata["outputs"], list)

    def test_bouncing_ball_has_position_output(self, bouncing_ball_fmu):
        from fmu_executor import read_fmu_metadata

        metadata = read_fmu_metadata(bouncing_ball_fmu)
        output_names = [o["name"] for o in metadata["outputs"]]

        # BouncingBall should have height/position output
        assert len(output_names) > 0

    def test_invalid_fmu_raises_error(self, fixtures_dir):
        from fmu_executor import read_fmu_metadata

        with pytest.raises(Exception):
            read_fmu_metadata(os.path.join(fixtures_dir, "nonexistent.fmu"))


class TestBuildInputArray:
    """Tests for converting CSV data to numpy structured array."""

    def test_build_input_array_basic(self, sample_input_data):
        from fmu_executor import build_input_array

        input_names = ["x", "y"]
        arr = build_input_array(sample_input_data, input_names)

        # Should be structured numpy array
        assert isinstance(arr, np.ndarray)
        assert arr.dtype.names is not None
        assert "time" in arr.dtype.names
        assert "x" in arr.dtype.names
        assert "y" in arr.dtype.names

    def test_build_input_array_values(self, sample_input_data):
        from fmu_executor import build_input_array

        input_names = ["x", "y"]
        arr = build_input_array(sample_input_data, input_names)

        assert arr[0]["time"] == 0.0
        assert arr[0]["x"] == 1.0
        assert arr[0]["y"] == 2.0
        assert len(arr) == 3

    def test_build_input_array_empty_inputs(self):
        from fmu_executor import build_input_array

        # FMU with no inputs - should return None
        arr = build_input_array([], [])
        assert arr is None

    def test_build_input_array_missing_column(self, sample_input_data):
        from fmu_executor import build_input_array

        # Request a column that doesn't exist - should use 0.0 as default
        input_names = ["x", "z"]  # z doesn't exist
        arr = build_input_array(sample_input_data, input_names)

        assert arr[0]["z"] == 0.0


class TestRunFmuSimulation:
    """Tests for running FMU simulation."""

    def test_run_bouncing_ball_simulation(self, bouncing_ball_fmu, sample_config):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],  # BouncingBall has no inputs
            config={"start_time": 0.0, "stop_time": 3.0}
        )

        assert "input_data" in result
        assert "status" in result
        assert result["status"] == "completed"
        assert len(result["input_data"]) > 0

    def test_simulation_output_has_time(self, bouncing_ball_fmu):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={"start_time": 0.0, "stop_time": 1.0}
        )

        # Each row should have time
        assert "time" in result["input_data"][0]

    def test_simulation_output_has_position(self, bouncing_ball_fmu):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={"start_time": 0.0, "stop_time": 1.0}
        )

        # Should have position for validator compatibility
        assert "position" in result["input_data"][0]

    def test_simulation_error_handling(self, fixtures_dir):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=os.path.join(fixtures_dir, "nonexistent.fmu"),
            input_data=[],
            config={}
        )

        assert result["status"] == "error"
        assert result["error_message"] is not None

    def test_simulation_with_parameter_override(self, bouncing_ball_fmu):
        """Test that parameters can be overridden via config."""
        from fmu_executor import run_fmu_simulation

        # Run with default gravity (-9.81)
        result_default = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={"start_time": 0.0, "stop_time": 2.0}
        )

        # Run with moon gravity (~-1.62)
        result_moon = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={
                "start_time": 0.0,
                "stop_time": 2.0,
                "parameters": {"g": -1.62}
            }
        )

        assert result_default["status"] == "completed"
        assert result_moon["status"] == "completed"

        # Ball should fall slower with weaker gravity
        # Compare position at same time point (around t=0.5)
        def get_position_at_time(data, target_time):
            for row in data:
                if abs(row["time"] - target_time) < 0.1:
                    return row["position"]
            return None

        pos_default = get_position_at_time(result_default["input_data"], 0.5)
        pos_moon = get_position_at_time(result_moon["input_data"], 0.5)

        # With weaker gravity, ball should be higher (fall slower)
        assert pos_moon > pos_default

    def test_simulation_with_invalid_parameter_ignored(self, bouncing_ball_fmu):
        """Test that invalid parameters are ignored without error."""
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={
                "start_time": 0.0,
                "stop_time": 1.0,
                "parameters": {"nonexistent_param": 123}
            }
        )

        # Should complete successfully, ignoring invalid parameter
        assert result["status"] == "completed"


class TestFormatOutput:
    """Tests for output format compatibility with simulink-runner."""

    def test_output_format_has_required_fields(self, bouncing_ball_fmu):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={"start_time": 0.0, "stop_time": 1.0}
        )

        # Should have all fields expected by downstream services
        assert "input_data" in result
        assert "status" in result
        # These will be added by main.py, but executor should not break them
        assert isinstance(result["input_data"], list)

    def test_position_values_are_numeric(self, bouncing_ball_fmu):
        from fmu_executor import run_fmu_simulation

        result = run_fmu_simulation(
            fmu_path=bouncing_ball_fmu,
            input_data=[],
            config={"start_time": 0.0, "stop_time": 1.0}
        )

        for row in result["input_data"]:
            if "position" in row:
                assert isinstance(row["position"], (int, float))
