import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {combineLatest, filter, map, Observable, of, take} from "rxjs";
import {WebcamImage} from "ngx-webcam";

@Injectable({
  providedIn: 'root'
})
export class QuixService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  private workingLocally = false; // set to true if working locally
  private token: string = ""; // Create a token in the Tokens menu and paste it here
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  public topic: string = ''; // get topic name from the Topics page in Quix portal
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  private domain = "";
  readonly server = ""; // leave blank
  private lat = 0
  private long = 0;

  private domainRegex = new RegExp("^https:\\/\\/portal-api\\.([a-zA-Z]+)\\.quix\\.ai")
  private readyToSend: boolean = false;
  private baseWriterUrl: string;

  constructor(private httpClient: HttpClient) {

    if(this.workingLocally) {
      this.domain = "platform"; // default to prod
      return;
    }

    const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');

    let sdkToken$ = this.httpClient.get(this.server + "sdk_token", {headers, responseType: 'text'});
    let topic$ = this.httpClient.get(this.server + "topic_raw", {headers, responseType: 'text'});
    let workspaceId$ =  this.httpClient.get(this.server + "workspace_id", {headers, responseType: 'text'});
    let portalApi$ = this.httpClient.get(this.server + "portal_api", {headers, responseType: 'text'})

    let value$ = combineLatest(
        sdkToken$,
        topic$,
        workspaceId$,
        portalApi$
    ).pipe(map(([sdkToken, topic, workspaceId, portalApi])=>{
      return {sdkToken, topic, workspaceId, portalApi};
    }));

    value$.subscribe(vals => {
      this.token = (vals.sdkToken).replace("\n", "");
      this.workspaceId = (vals.workspaceId).replace("\n", "");
      this.topic = (this.workspaceId + "-" + vals.topic).replace("\n", "");

      let portalApi = vals.portalApi.replace("\n", "");
      let matches = portalApi.match(this.domainRegex);
      if(matches) {
        this.domain = matches[1];
      }
      else {
        this.domain = "platform"; // default to prod
      }

      // don't change this
      this.baseWriterUrl = "https://writer-" + this.workspaceId + "." + this.domain + ".quix.ai/";

      this.readyToSend = true;
    });

  }

  sendScreenshotData(workspaceId: string, tokenId: string, topicId: string, body: any) {
    let headers = new HttpHeaders();
    headers = headers.set('Authorization', `Bearer ${tokenId}`);
    headers = headers.set('Content-Type', 'application/json');
    return this.httpClient.post(this.baseWriterUrl + `topics/${topicId}/streams/input-image/parameters/data`, body, { headers });
  }

  /**
   * Get all the required data needed to send the image + geolocation
   * coords to Quix so that it can be transformed before being displayed
   * on the dashboard.
   */
  sendDataToQuix(webcamImage: WebcamImage): void {

    if(!this.readyToSend){
      return;
    }

    this.getGeoLocation();
    //this.trigger.next(); //todo

    console.log('Sending data to Quix via the writer API: ', this.token, this.domain, this.workspaceId, this.topic);
    const body = JSON.stringify(
        {
          Timestamps: [new Date().getTime() * 1000000],
          StringValues: {"image": [webcamImage.imageAsBase64]},
          NumericValues: {"lat": [this.lat], "lon": [this.long]}
        }
    )
    // Send the data to Quix
    this.sendScreenshotData(this.workspaceId, this.token, this.topic, body)
        .pipe(take(1)).subscribe(() => {
      console.log('Image + coords successfully sent!')
    })
  }

  /**
   * Using the built in browser navigator,
   * retrieve the user's geo location.
   * @returns
   */
  private getGeoLocation(): void {
    // First check if the Geolocation API is supported
    if (!navigator.geolocation) {
      console.log(`Your browser doesn't support Geolocation`);
      return;
    }

    // If so, then get the geo location of user
    navigator.geolocation.getCurrentPosition((position) => {
      const { latitude, longitude } = position.coords;
      this.lat = latitude;
      this.long = longitude;
    });
  }


}
