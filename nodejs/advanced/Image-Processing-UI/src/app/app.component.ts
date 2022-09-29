/// <reference types="@types/googlemaps" />

import {Component, OnInit } from '@angular/core';
import {HubConnectionBuilder} from "@microsoft/signalr";
import {ParameterData} from "./models/parameter-data";
import {EnvironmentVariablesService} from "./services/environment-variables.service"
import {forkJoin} from "rxjs";
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'mobile-tracker';

  colors = [
      '#FFE8CC',
      '#FB8804',
      '#7FBD32',
      '#6F0CBB',
      '#6F0CBB',
      '#9E9E9E',
    ]

  private token: string;
  private topic: string;
  private workspaceId: string;

  vehicles: { [streamId: string]: VehicleItem } = {}
  lat: number = 51.678418;
  lng: number = 7.809007;
  public connected: boolean;
  public map: any;
  public reconnecting: boolean;
  public last_image: string;
  public cameras = {}

  constructor(private envVarService: EnvironmentVariablesService) {}

  ngOnInit(): void {

    console.log("INIT APP.Component");

    this.token = this.envVarService.Token;
    this.topic = this.envVarService.Topic;
    this.workspaceId = this.envVarService.WorkspaceId;

    console.log("1Token:" + this.token);
    console.log("1Topic:" + this.topic);
    console.log("1WS:" + this.workspaceId);

    // get all this stuff
    let values$ = forkJoin(
        this.envVarService.GetToken(),
        this.envVarService.GetTopic(),
        this.envVarService.GetWorkspaceId(),
    ).pipe(
        map(([token, topic, wsId])=>{
            console.log(token);
            console.log(topic);
            console.log(wsId);
          return {token, topic, wsId};
        })
    );

    // when it arrives, connect to Quix
    values$.subscribe(x => {
        let url = this.envVarService.buildUrl(x.wsId)
        this.ConnectToQuix(x.token, x.topic, url);
    });

  }

  onMapReady(map: any ) {
    this.map = map;
  }

    connection = undefined;
    ConnectToQuix(quixToken, quixTopic, readerUrl): void{

        const options = {
            accessTokenFactory: () => quixToken
        };

        this.connection = new HubConnectionBuilder()
            .withAutomaticReconnect()
            .withUrl(readerUrl, options)
            .build();

        this.connection.onreconnecting(e => {
            this.connected = false;
            this.reconnecting = true;
        });
        this.connection.onreconnected(e => {
            this.connected = true;
            this.reconnecting = false;
        });
        this.connection.onclose(e => {
            this.connected = false;
            this.reconnecting = false;
        });

        this.connection.start().then(() => {
            console.log("SignalR connected.");

            this.connected = true;

            this.connection.on("ParameterDataReceived", (data: ParameterData) => {
                let imageBinary = data.stringValues["image"][0];
                //let buffer = new Buffer(imageBinary);
                //let encoded = buffer.toString('base64')
                this.last_image = "data:image/png;base64," + imageBinary;

                var mIcon = {
                    path: google.maps.SymbolPath.CIRCLE,
                    fillOpacity: 1,
                    fillColor: '#fff',
                    strokeOpacity: 1,
                    strokeWeight: 1,
                    strokeColor: '#333',
                    scale: 12
                };

                let cameraId = data.tagValues["parent_streamId"][0]

                if (cameraId in this.cameras){
                    this.cameras[cameraId].label.text = data.numericValues["car"][0].toString();
                    console.log("UPDATE");
                }
                else{
                    var gMarker = new google.maps.Marker({
                        map: this.map,
                        position: {
                            lat: data.numericValues["lat"][0],
                            lng: data.numericValues["lon"][0]
                        },
                        title: 'Number 123',
                        icon: mIcon,
                        label: {color: '#000', fontSize: '12px', fontWeight: '600',
                            text:  data.numericValues["car"][0].toString()}
                    });
                }

                this.map.setma
            });

            //"image-proccessed-merged"
            this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "image");
            this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lat");
            this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "car");
            this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lon");
        });
    }


}

export class VehicleItem {
  lat?: number;
  lng?: number;
  speed?: number;
  lastPosition?: Date;
  name: string;
  color:string;
  wear: number;
  tail: { lat: number, lng: number }[]
}
