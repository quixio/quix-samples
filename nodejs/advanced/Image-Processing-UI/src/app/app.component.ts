import { Component, OnInit } from '@angular/core';
import { HubConnection } from "@microsoft/signalr";
import { ParameterData } from "./models/parameter-data";
import { QuixService } from "./services/quix.service"
import { MatSelectChange } from '@angular/material/select';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  popularObjectTypes = ['bicycle', 'bus', 'car', 'motorbike', 'person', 'traffic light', 'truck'];
  otherObjectTypes = ['aeroplane', 'apple', 'banana', 'backpack', 'bed', 'bench', 'bird', 'boat', 'book', 'bottle', 'bowl', 'broccoli', 'cake', 'carrot', 'cat'];

  private topic: string;

  latitude: number = 51.5072;
  longitude: number = -0.1000;
  public map: any;
  public last_image: string;
  private markers: any[] = new Array();
  connection: HubConnection;
  selectedObject: string = "";

  constructor(private envVarService: QuixService) { }

  ngOnInit(): void {
    console.log("INIT APP.Component");

    this.envVarService.InitCompleted.subscribe(topic => {
      console.log("Init completed: " + topic);
      this.topic = topic;
      this.envVarService.ConnectToQuix().then(connection => {
        this.connection = connection;
        this.subscribeToData(topic);
      });
    });

    if(this.envVarService.workingLocally){
      this.topic = this.envVarService.topic;
      this.envVarService.ConnectToQuix().then(connection => {
        this.connection = connection;
        this.subscribeToData(this.topic);
      });
    }

    this.selectedObject = "car";
  }

  /**
   * Using the topic, we can subscribe to the data being outputted
   * by quix.
   * 
   * @param quixTopic the topic we want to retrieve data for
   */
  subscribeToData(quixTopic: string) {
    this.connection.on("ParameterDataReceived", (data: ParameterData) => {
      if (data.stringValues["image"]) {
        let imageBinary = data.stringValues["image"][0];
        this.last_image = "data:image/png;base64," + imageBinary;
      }

      var markerIcon = {
        path: google.maps.SymbolPath.CIRCLE,
        fillOpacity: 1,
        fillColor: '#fff',
        strokeOpacity: 1,
        strokeWeight: 1,
        strokeColor: '#333',
        scale: 12
      };

      var gMarker = new google.maps.Marker({
        map: this.map,
        position: {
          lat: data.numericValues["lat"][0],
          lng: data.numericValues["lon"][0]
        },
        title: 'Number 123',
        icon: markerIcon,
        label: {
          color: '#000', fontSize: '12px', fontWeight: '600',
          text: data.numericValues[this.selectedObject][0].toString()
        }
      });

      this.markers.push(gMarker);
      if (this.markers.length > 1000) {
        this.markers.shift();
      }

    });

    this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "image");
    this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lat");
    this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", this.selectedObject);
    this.connection.invoke("SubscribeToParameter", quixTopic, "image-feed", "lon");
  }

  /**
   * Triggered when the map is initialized.
   * @param map the map object
   */
  onMapReady(map: any) {
    this.map = map;
  }

  showImages: boolean = true;

  /**
   * Loop through old markers and remove them from the map
   * for the new selected object. Also unsubscribes from the old
   * selected parameter and subscribes to the new.

  * @param newSelectedObject the newly selected object
   */
  public selectedObjectChanged(event: MatSelectChange) {
    const { value } = event;
    for (let i = 0; i < this.markers.length; i++) {
      this.markers[i].setMap(null);
    }
    this.connection?.invoke("UnsubscribeFromParameter", this.topic, "image-feed", this.selectedObject);
    this.connection?.invoke("SubscribeToParameter", this.topic, "image-feed", value);
    this.selectedObject = value;
  }

  /**
   * Toggles the feed stream.
   * 
   * If it's currently running then unsubscribe from the parameter.
   * Else we can resubscribe to it to resume retrieving data. 
   */
  public toggleFeed() {
    this.showImages =! this.showImages;
    if (!this.showImages) {
      this.connection.invoke("UnsubscribeFromParameter", this.topic, "image-feed", "image");
    }
    else {
      this.connection.invoke("SubscribeToParameter", this.topic, "image-feed", "image");
    }
  }
}