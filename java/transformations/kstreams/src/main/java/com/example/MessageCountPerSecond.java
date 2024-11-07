package com.example;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.KStream;
import org.apache.kafka.streams.kstream.KTable;
import org.apache.kafka.streams.kstream.TimeWindows;
import org.apache.kafka.streams.kstream.Windowed;
import org.apache.kafka.streams.kstream.Produced;
import org.json.JSONObject;

import java.io.IOException;
import java.time.Duration;
import java.util.Properties;

public class MessageCountPerSecond {

    public static void main(String[] args) {
        try {

            String workspace_id = System.getenv("Quix__Workspace__Id");

            // Get Kafka configuration properties
            Properties props = QuixConfigBuilder.buildKafkaProperties();

            props.put("application.id", "message-count-app");
            props.put("default.key.serde", "org.apache.kafka.common.serialization.Serdes$StringSerde");
            props.put("default.value.serde", "org.apache.kafka.common.serialization.Serdes$StringSerde");

            StreamsBuilder builder = new StreamsBuilder();
            KStream<String, String> messageStream = builder.stream( workspace_id + "-" + System.getenv("input"));

            // Count messages per second
            KTable<Windowed<String>, Long> messageCountPerSecond = messageStream
                    .groupByKey()
                    .windowedBy(TimeWindows.of(Duration.ofSeconds(1)))
                    .count();

            // Convert the count data to JSON format before sending it to the output topic
            KStream<String, String> jsonOutputStream = messageCountPerSecond.toStream()
                    .map((windowedKey, count) -> {
                        long windowStart = windowedKey.window().start();
                        long windowEnd = windowedKey.window().end();

                        // Create a JSON object with window-start, window-end, and count
                        JSONObject jsonObject = new JSONObject();
                        jsonObject.put("window-start", windowStart);
                        jsonObject.put("window-end", windowEnd);
                        jsonObject.put("count", count);

                        // Convert the Windowed key to a simple string representation (optional)
                        String key = windowedKey.key();

                        // Return the new key-value pair where value is JSON string
                        return new org.apache.kafka.streams.KeyValue<>(key, jsonObject.toString());
                    });

            // Output the JSON results to another topic
            jsonOutputStream.to(workspace_id + "-" + System.getenv("output"), Produced.with(Serdes.String(), Serdes.String()));

            KafkaStreams streams = new KafkaStreams(builder.build(), props);
            streams.start();

            // Gracefully shutdown on exit
            Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        } catch (IOException | InterruptedException e) {
            e.printStackTrace();
            System.exit(1);
        }
    }
}