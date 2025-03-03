print("Starting matlab")

import matlab.engine

eng = matlab.engine.start_matlab()

output = eng.sqrt(8.0)

print (output)