"""
FMU Executor - Core FMU simulation execution logic

Handles:
- Reading FMU model description
- Building input arrays from CSV data
- Running simulations using fmpy
- Converting results to output format compatible with simulink-runner
"""
import os
import logging
from typing import Optional, Dict, List, Any
import numpy as np
from fmpy import read_model_description, simulate_fmu

logger = logging.getLogger(__name__)

# Supported file extensions for this runner
SUPPORTED_EXTENSIONS = {'.fmu'}


def should_process(filename: Optional[str]) -> bool:
    """
    Check if this runner should process the given model file.

    Args:
        filename: Model filename to check

    Returns:
        True if this is an FMU file, False otherwise
    """
    if not filename:
        return False
    ext = os.path.splitext(filename)[1].lower()
    return ext in SUPPORTED_EXTENSIONS


def read_fmu_metadata(fmu_path: str) -> Dict[str, Any]:
    """
    Read FMU model description and extract variable information.

    Args:
        fmu_path: Path to the FMU file

    Returns:
        Dictionary with inputs, outputs, and parameters lists
    """
    md = read_model_description(fmu_path)

    inputs = []
    outputs = []
    parameters = []

    for v in md.modelVariables:
        var_info = {
            'name': v.name,
            'valueReference': v.valueReference,
            'description': getattr(v, 'description', None),
            'type': v.type,
            'start': getattr(v, 'start', None),
            'causality': v.causality,
            'variability': getattr(v, 'variability', None),
        }

        if v.causality == 'input':
            inputs.append(var_info)
        elif v.causality == 'output':
            outputs.append(var_info)
        elif v.causality == 'parameter':
            parameters.append(var_info)

    return {
        'inputs': inputs,
        'outputs': outputs,
        'parameters': parameters,
        'fmi_version': md.fmiVersion,
        'model_name': md.modelName,
        'description': getattr(md, 'description', None),
    }


def build_input_array(
    input_data: List[Dict[str, Any]],
    input_names: List[str]
) -> Optional[np.ndarray]:
    """
    Convert CSV-style input data to numpy structured array for fmpy.

    Args:
        input_data: List of dicts with column values (CSV rows)
        input_names: List of FMU input variable names

    Returns:
        Structured numpy array with 'time' + input columns, or None if no inputs
    """
    if not input_data or not input_names:
        return None

    # Build dtype: time + all input names
    dtype_fields = [('time', np.float64)]
    for name in input_names:
        dtype_fields.append((name, np.float64))

    # Build data rows
    data_rows = []
    for row in input_data:
        time_val = float(row.get('time', 0.0))
        values = [time_val]
        for name in input_names:
            # Use 0.0 as default if column doesn't exist
            values.append(float(row.get(name, 0.0)))
        data_rows.append(tuple(values))

    return np.array(data_rows, dtype=dtype_fields)


def run_fmu_simulation(
    fmu_path: str,
    input_data: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute FMU simulation and return results in standard format.

    Args:
        fmu_path: Path to the FMU file
        input_data: Input time series data (list of dicts)
        config: Simulation configuration with start_time, stop_time, parameters, etc.
            - start_time: Simulation start time (default 0.0)
            - stop_time: Simulation stop time (default 10.0)
            - parameters: Dict of parameter name -> value to override defaults

    Returns:
        Dict with 'input_data', 'status', and optionally 'error_message'
    """
    try:
        # Read model metadata
        metadata = read_fmu_metadata(fmu_path)
        input_names = [v['name'] for v in metadata['inputs']]
        output_names = [v['name'] for v in metadata['outputs']]
        param_names = [v['name'] for v in metadata['parameters']]

        # Build type lookup for outputs
        output_types = {}
        for v in metadata.get('outputs', []):
            output_types[v['name']] = get_fmu_type_name(v.get('type'))

        # Filter out String outputs - fmpy can't return them in structured array
        numeric_output_names = [
            name for name in output_names
            if output_types.get(name, 'Real') != 'String'
        ]
        if len(numeric_output_names) < len(output_names):
            skipped = [n for n in output_names if n not in numeric_output_names]
            logger.info(f"  Skipping String outputs (not supported by fmpy): {skipped}")

        logger.info(f"Running FMU simulation: {fmu_path}")
        logger.info(f"  Inputs: {input_names}")
        logger.info(f"  Outputs: {output_names}")
        logger.info(f"  Parameters: {param_names}")

        # Build input array if we have inputs
        input_array = None
        if input_data and input_names:
            input_array = build_input_array(input_data, input_names)
            start_time = float(input_array['time'][0])
            stop_time = float(input_array['time'][-1])
        else:
            start_time = config.get('start_time', 0.0)
            stop_time = config.get('stop_time', 10.0)

        # Build simulation kwargs
        sim_kwargs = {
            'filename': fmu_path,
            'start_time': start_time,
            'stop_time': stop_time,
        }

        # Add output selection if we have outputs (only numeric types)
        if numeric_output_names:
            sim_kwargs['output'] = numeric_output_names

        # Add input array if we have inputs
        if input_array is not None and len(input_array) > 0:
            sim_kwargs['input'] = input_array

        # Add parameter overrides if specified in config
        parameters = config.get('parameters', {})
        if parameters:
            # Validate that parameters exist in the FMU
            valid_params = {}
            for name, value in parameters.items():
                if name in param_names:
                    valid_params[name] = float(value)
                    logger.info(f"  Setting parameter {name} = {value}")
                else:
                    logger.warning(f"  Unknown parameter '{name}' ignored (valid: {param_names})")
            if valid_params:
                sim_kwargs['start_values'] = valid_params

        # Run simulation
        result = simulate_fmu(**sim_kwargs)

        # Log what columns are in the result for debugging
        logger.info(f"  Result columns from fmpy: {list(result.dtype.names)}")
        logger.info(f"  Expected output names: {numeric_output_names}")

        # Convert results to output format (only numeric outputs)
        output_data = format_output(result, numeric_output_names, metadata)

        return {
            'input_data': output_data,
            'status': 'completed',
            'error_message': None,
        }

    except Exception as e:
        logger.error(f"FMU simulation failed: {e}")
        return {
            'input_data': [],
            'status': 'error',
            'error_message': str(e),
        }


def get_fmu_type_name(fmu_type) -> str:
    """
    Extract type name string from FMU type object.

    Args:
        fmu_type: Type object from FMU model description

    Returns:
        Type name as string: 'Real', 'Integer', 'Boolean', 'String', or 'Unknown'
    """
    if fmu_type is None:
        return 'Real'
    type_name = type(fmu_type).__name__
    if type_name in ('Real', 'Integer', 'Boolean', 'String'):
        return type_name
    return 'Real'


def convert_output_value(val, fmu_type: str):
    """
    Convert numpy value to Python native type with type preservation.

    Args:
        val: Value from numpy array
        fmu_type: FMU type name ('Real', 'Integer', 'Boolean', 'String')

    Returns:
        Python native value with appropriate type
    """
    if val is None:
        return None

    if fmu_type == 'Integer':
        return int(val)
    elif fmu_type == 'Boolean':
        return bool(val)
    elif fmu_type == 'String':
        return str(val)
    else:
        # Real or unknown - use float
        return float(val)


def format_output(
    result: np.ndarray,
    output_names: List[str],
    metadata: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Convert fmpy result array to list of dicts with type preservation.

    Maps the first numeric output to 'position' for backward compatibility
    with the validator's legacy mode.

    Args:
        result: Structured numpy array from simulate_fmu
        output_names: List of output variable names
        metadata: FMU metadata dict

    Returns:
        List of dicts with time and output values (types preserved)
    """
    output_data = []

    # Build type lookup from metadata
    output_types = {}
    for v in metadata.get('outputs', []):
        output_types[v['name']] = get_fmu_type_name(v.get('type'))

    for i in range(len(result)):
        row = {'time': float(result['time'][i])}

        # Add all output values with type preservation
        for name in output_names:
            if name in result.dtype.names:
                val = result[name][i]
                fmu_type = output_types.get(name, 'Real')

                # Handle array-valued outputs
                if hasattr(val, '__len__') and not isinstance(val, str):
                    row[name] = [convert_output_value(v, fmu_type) for v in val]
                else:
                    row[name] = convert_output_value(val, fmu_type)

        # Map first numeric output to 'position' for validator backward compatibility
        # Only use numeric types (Real, Integer) for position
        position_candidates = ['h', 'height', 'position', 'x', 'y', 'z', 'displacement']
        position_found = False

        for candidate in position_candidates:
            if candidate in row and output_types.get(candidate, 'Real') in ('Real', 'Integer'):
                row['position'] = float(row[candidate])
                position_found = True
                break

        # If no known position field, use first numeric output
        if not position_found and output_names:
            for name in output_names:
                if name in row and output_types.get(name, 'Real') in ('Real', 'Integer'):
                    row['position'] = float(row[name])
                    break

        output_data.append(row)

    return output_data
