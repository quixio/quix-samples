from quixstreams import Application
from fmpy import read_model_description, extract, instantiate_fmu, simulate_fmu
import pandas as pd
import numpy as np
import os

# Check FMU model
fmu_filename = "simulink_example_inports.fmu"  # adjust if in another path

# 1) read model description (variable names, valueReferences, interface type)
print("FMU MODEL:")
md = read_model_description(fmu_filename)
print('FMI version:', md.fmiVersion)
for v in md.modelVariables:
    print(v.name, v.valueReference, v.causality)

# Define matlab function call
def FMU_processing(row: dict):
    x = row["x"]
    y = row["y"]
    theta = np.pi / 4  # 45 degrees in radians

    # Build structured input
    input_data = np.array(
        [(0.0, x, y, theta)], 
        dtype=[('time', np.float64),
               ('x', np.float64),
               ('y', np.float64),
               ('theta', np.float64)]
    )

    result = simulate_fmu(
        fmu_filename,
        start_time=0.0,
        stop_time=0.0,
        input=input_data
    )

    result_df = pd.DataFrame.from_records(result)

    # Convert to standard Python float for JSON serialization
    row["x_new"] = float(result_df["Out1"][0])
    row["y_new"] = float(result_df["Out2"][0])
    

def main():
    # Setup necessary objects
    app = Application(
        consumer_group="FMU-Model-Run",
        auto_create_topics=True,
        auto_offset_reset="earliest"
    )
    input_topic = app.topic(name=os.environ["input"])
    output_topic = app.topic(name=os.environ["output"])
    sdf = app.dataframe(topic=input_topic)
    

    # Do StreamingDataFrame operations/transformations here
    #sdf.print_table()
    sdf = sdf.update(FMU_processing)
    sdf.print_table()

    # Finish off by writing to the final result to the output topic
    sdf.to_topic(output_topic)

    # With our pipeline defined, now run the Application
    app.run()


# It is recommended to execute Applications under a conditional main
if __name__ == "__main__":
    main()