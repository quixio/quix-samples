/// <reference types="@types/googlemaps" />

import {Component, OnInit} from '@angular/core';
import {HubConnectionBuilder} from "@microsoft/signalr";
import {ParameterData} from "./models/parameter-data";
import {EnvironmentVariablesService} from "./services/environment-variables.service"
import {combineLatest} from "rxjs";
import {map} from 'rxjs/operators';
import {ActivatedRoute} from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'mobile-tracker';

  objectTypes = ['person', 'bicycle', 'car', 'motorbike', 'aeroplane', 'bus', 'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'sofa', 'pottedplant', 'bed', 'diningtable', 'toilet', 'tvmonitor', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush']

  colors = [
      '#FFE8CC',
      '#FB8804',
      '#7FBD32',
      '#6F0CBB',
      '#6F0CBB',
      '#9E9E9E',
    ]

  private topic: string;

  lat: number = 51.5072;
  lng: number = -0.1000;
  public connected: boolean;
  public map: any;
  public reconnecting: boolean;
  public last_image: string;
  public cameras = {};
  private markers: any[] = new Array();
  public showTokenWarning: boolean = false;

  constructor(private envVarService: EnvironmentVariablesService,
              private route: ActivatedRoute) {}

  ngOnInit(): void {

      console.log("INIT APP.Component");

      // get all this stuff
      let values$ = combineLatest(
          this.envVarService.GetToken(),
          this.envVarService.GetTopic(),
          this.envVarService.GetWorkspaceId(),
          this.route.queryParams
      ).pipe(
          map(([token, topic, wsId, params]) => {
              return {token, topic, wsId, params};
          })
      );

      // when it arrives, connect to Quix
      values$.subscribe(x => {

          let wsid = x.wsId.replace(/\n|\r/g, "");
          let top = x.topic.replace(/\n|\r/g, "");
          let tok = x.token.replace(/\n|\r/g, "");

          let url = this.envVarService.buildUrl(wsid)
          if (tok == "") {
              this.showTokenWarning = true;
          }
          this.topic = top;

          if(x.params["token"] !== undefined){
              tok = x.params["token"];
          }

          console.log(tok);
          console.log(top);
          console.log(wsid);
          console.log(url);

          this.ConnectToQuix(tok, top, url).then(_ => {
              this.subscribeToData(top);
          });
      });

      this.selectedObject = "car";
  }

  subscribeToData(quixTopic){
      this.connection.on("ParameterDataReceived", (data: ParameterData) => {
          if (data.stringValues["image"]) {
              let imageBinary = data.stringValues["image"][0];
              this.last_image = "data:image/png;base64," + imageBinary;
          }

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
              this.cameras[cameraId].label.text = data.numericValues[this.selectedObject][0].toString();
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
                      text:  data.numericValues[this.selectedObject][0].toString()}
              });
              this.markers.push(gMarker);
              if(this.markers.length > 1000){
                  this.markers.shift();
              }
          }
          this.map.setma
      });

      this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "image");
      this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lat");
      this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", this.selectedObject);
      this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lon");
  }

  onMapReady(map: any ) {
    this.map = map;
  }

    connection = undefined;
    selectedObject: string = "";
    ConnectToQuix(quixToken, quixTopic, readerUrl): Promise<void>{

        if (this.connected){
            return Promise.resolve();
        }

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

        return this.connection.start().then(() => {
            console.log("SignalR connected.");

            this.connected = true;

            return
        });
    }

    startStopButtonText: string = "Stop image feed";
    showImages: boolean = true;

    selectedObjectChanged(newObject) {
        for (let i=0; i< this.markers.length; i++) {
            this.markers[i].setMap(null);
        }
        this.connection.invoke("UnsubscribeFromParameter", this.topic, "image-feed", this.selectedObject);
        this.connection.invoke("SubscribeToParameter", this.topic, "image-feed", newObject);
    }

    startStopButtonClick() {

        if(this.showImages){
            this.showImages = false;
            this.startStopButtonText = "Start image feed";
            this.connection.invoke("UnsubscribeFromParameter", this.topic, "image-feed", "image");
        }
        else {
            this.showImages = true;
            this.startStopButtonText = "Stop image feed";
            this.connection.invoke("SubscribeToParameter", this.topic, "image-feed", "image");
        }
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
