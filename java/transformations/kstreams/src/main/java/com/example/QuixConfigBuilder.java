package com.example;

import org.apache.kafka.common.protocol.types.Field.Str;
import org.json.JSONObject;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Properties;

public class QuixConfigBuilder {


    // API URL to get Kafka configuration from QuixCloud.
    private static final String KAFKA_CONFIG_API_URL = "%s/workspaces/%s/broker/librdkafka";

    /// <summary>
    /// Builds Kafka configuration properties using the QuixCloud API.
    /// </summary>
    public static Properties buildKafkaProperties() throws IOException, InterruptedException {

        // Environment variables provided by QuixCloud runtime
        String workspaceId = System.getenv("Quix__Workspace__Id");
        String token = System.getenv("Quix__Sdk__Token");
        String portalApi = System.getenv("Quix__Portal__Api");
        
    
        HttpClient client = HttpClient.newHttpClient();

        // API Call to get Kafka configuration
        HttpRequest kafkaConfigRequest = HttpRequest.newBuilder()
                .uri(URI.create(String.format(KAFKA_CONFIG_API_URL, portalApi, workspaceId)))
                .header("accept", "text/plain")
                .header("X-Version", "2.0")
                .header("Authorization", "bearer " + token)
                .build();

        HttpResponse<String> kafkaConfigResponse = client.send(kafkaConfigRequest, HttpResponse.BodyHandlers.ofString());

        // Parse the JSON response
        JSONObject jsonResponse = new JSONObject(kafkaConfigResponse.body());
        String bootstrapServers = jsonResponse.getString("bootstrap.servers");
        String securityProtocol = jsonResponse.getString("security.protocol");
        String saslMechanism = jsonResponse.getString("sasl.mechanism");
        String saslUsername = jsonResponse.getString("sasl.username");
        String saslPassword = jsonResponse.getString("sasl.password");
        String clientId = jsonResponse.getString("client.id");

        // Set up Kafka Streams configuration properties
        Properties props = new Properties();
        props.put("bootstrap.servers", bootstrapServers);
        props.put("security.protocol", securityProtocol);
        props.put("sasl.mechanism", saslMechanism);
        props.put("sasl.jaas.config", String.format(
                "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"%s\" password=\"%s\";",
                saslUsername, saslPassword));
        props.put("client.id", clientId);

        return props;
    }
}