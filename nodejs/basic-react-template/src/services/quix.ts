import * as signalR from '@microsoft/signalr';
import {HubConnection, HubConnectionState} from '@microsoft/signalr';
import {Stream} from "../Models/stream";
import { Event, QuixEvent } from '../Models/event';
import { ParameterData } from '../Models/parameterData';
import { Data } from '../Models/data';

import axios from 'axios';


export enum HubType {
    Reader = "reader",
    Writer = "writer"
}

export class QuixLiveService  {

    public readerHubConnection: HubConnection;
    public writerHubConnection: HubConnection;

    /*Working Locally? - set these values*/
    private workingLocally = false;
    private token = '';
    private workspaceId: string = "";
    private subdomain = "platform";


    public async getWorkspaceIdAndToken(doneCallback): Promise<void>{
        console.log("Running getWorkspaceIdAndToken")

        this.token = (await this.fetchConfig("bearer_token")).value;
        this.workspaceId = (await this.fetchConfig("workspace_id")).value;
    }

    public async fetchConfig(config_setting): Promise<{ value: string }> {
        try {
            const headers = {
                'Content-Type': 'application/json',
                // Add other headers as needed
            };

            // leave blank for normal operation, set to some server or api url to get settings from there
            // leaving blank will, when deployed in Quix, get config from files in the local file system
            // see run_server.sh for which environment values are copied to files at runtime.
            const override_server = ""

            const response = await axios.get(override_server + config_setting, { headers, responseType: 'text' })
                .catch(error => {
                    console.error('Axios request failed:', error);
                    throw error;
                });
            // Check status code and throw error for unsuccessful status codes
            if (response.status < 200 || response.status >= 300) {
                throw new Error(`HTTP request failed with status code ${response.status}`);
            }

            // Log the response
            console.log(response);

            let value = response.data.replace(/(\r\n|\n|\r)/gm, ""); // This line removes all line breaks
            return { value };
        } catch (error) {
            console.error('Error config value:', error);
            throw error;
        }
    }

    public async startConnection() : Promise<void>{

        // connect reader
        this.readerHubConnection = await this.connect(HubType.Reader);
        
        //connect writer
        this.writerHubConnection = await this.connect(HubType.Writer);

        console.log("SignalR connected.")
    }

    private async connect(type: HubType): Promise<HubConnection>{

        let hubConnection: HubConnection;

        let options = {
            accessTokenFactory: () => this.token
        };

        let url = "https://" + type + "-" + this.workspaceId + "." + this.subdomain + ".quix.io/hub";
        console.log("Creating SignalR hub connection to: " + url);
        hubConnection = new signalR.HubConnectionBuilder()
            .withUrl(url, options)
            .withAutomaticReconnect()
            .build();

        console.log("Starting connection");
        await hubConnection.start();

        return hubConnection;
    }

    public async subscribeToActiveStreams(activeStreamsChanged: (stream: Stream, actionType: string) => void, topic: string): Promise<Stream[]>{
        console.log("Using topic=" + topic + " to subscribe to streams..")
        
        let streams = await this.readerHubConnection.invoke("SubscribeToActiveStreams", topic);

        this.readerHubConnection.on("ActiveStreamsChanged", (stream: Stream, actionType: string) => {
            console.log(stream.name)
            activeStreamsChanged(stream, actionType);
        });
        return streams;
    }

    public async subscribeToEvents(eventReceived: (payload: QuixEvent) => void, topic: string, streamId: string, parameterId: string): Promise<Event[]>{
        let events = this.readerHubConnection.invoke("SubscribeToEvent", topic, streamId, parameterId);
    
        // Listen for event data and emit
        this.readerHubConnection.on("EventDataReceived", (payload: QuixEvent) => {
          eventReceived(payload);
        });
        return events;
      }


      public async subscribeToParameterData(dataReceived: (payload: ParameterData) => void, topic: string, streamId: string, parameterId: string): Promise<ParameterData[]>{
        let events = this.readerHubConnection.invoke("SubscribeToParameter", topic, streamId, parameterId);
    
        // Listen for event data and emit
        this.readerHubConnection.on("ParameterDataReceived", (payload: ParameterData) => {
            dataReceived(payload);
        });
        return events;
      }

      public sendParameterData(topic: string, streamId: string, payload: Data): void {
        console.log("QuixService Sending parameter data!", topic, streamId, payload);
        this.writerHubConnection.invoke("SendParameterData", topic, streamId, payload);
      }

      public unsubscribeFromParameter(topic: string, streamId: string, parameterId: string) {
        // console.log(`QuixService Reader | Unsubscribing from parameter - ${topic}, ${streamId}, ${parameterId}`);
        this.readerHubConnection.invoke("UnsubscribeFromParameter", topic, streamId, parameterId);
      }
    
      public unsubscribeFromEvent(topic: string, streamId: string, eventId: string) {
        // console.log(`QuixService Reader | Unsubscribing from event - ${topic}, ${streamId}, ${eventId}`);
        this.readerHubConnection.invoke("UnsubscribeFromEvent", topic, streamId, eventId);
      }
}

export const quixLiveService = new QuixLiveService();
