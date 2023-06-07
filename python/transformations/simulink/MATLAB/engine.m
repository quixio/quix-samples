function R = engine(throttle_angle, time)
    ta = timeseries(throttle_angle, time);
    assignin("base", "throttle_angle", ta);
    sim('sldemo_engine');
    R = engine_speed.Data(end);
end