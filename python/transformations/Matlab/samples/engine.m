function R = engine(throttle_angle, time)
    ta = timeseries(throttle_angle, time);
    assignin("base", "throttle_angle", ta);
    si = Simulink.SimulationInput('sldemo_engine');
    si = simulink.compiler.configureForDeployment(si);
    sout = sim(si);
    R = sout.engine_speed.Data(end);
end