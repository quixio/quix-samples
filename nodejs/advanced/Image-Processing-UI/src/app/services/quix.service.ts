import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {combineLatest, of, Subject} from "rxjs";
import {map} from "rxjs/operators";
import {HubConnection, HubConnectionBuilder} from "@microsoft/signalr";

@Injectable({
  providedIn: 'root'
})
export class QuixService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  public workingLocally = false; // set to true if working locally
  private token: string = ""; // Create a token in the Tokens menu and paste it here
  public workspaceId: string = ""; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  public topic: string = ""; // get topic name from the Topics page in Quix portal
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  private domain = "";
  readonly server = ""; // leave blank

  private domainRegex = new RegExp("^https:\\/\\/portal-api\\.([a-zA-Z]+)\\.quix\\.ai")
  private baseReaderUrl: string;
  private connection: HubConnection;
  InitCompleted: Subject<string> = new Subject<string>();

  constructor(private httpClient: HttpClient) {

    if(this.workingLocally) {
      this.domain = "platform"; // default to prod

      this.baseReaderUrl = "https://reader-" + this.workspaceId + "." + this.domain + ".quix.ai/hub";
      return;
    }

    const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');

    let sdkToken$ = this.httpClient.get(this.server + "sdk_token", {headers, responseType: 'text'});
    let topic$ = this.httpClient.get(this.server + "processed_topic", {headers, responseType: 'text'});
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
      this.baseReaderUrl = "https://reader-" + this.workspaceId + "." + this.domain + ".quix.ai/hub";

      this.InitCompleted.next(this.topic);
    });

  }

  /**
   * Makes the initial connection to Quix.
   *
   * If we have already connected then we can just return and
   * skip the process.
   *
   * @param quixToken the Quix token needed to authenticate the connection
   * @param readerUrl the Url we are connecting to
   * @returns
   */
  public ConnectToQuix(): Promise<HubConnection> {

    const options = {
      accessTokenFactory: () => this.token
    };

    this.connection = new HubConnectionBuilder()
        .withAutomaticReconnect()
        .withUrl(this.baseReaderUrl, options)
        .build();

    this.connection.onreconnecting(e => {
    });
    this.connection.onreconnected(e => {
    });
    this.connection.onclose(e => {
    });

    return this.connection.start().then(() => {
      console.log("Connected to Quix!");
      return this.connection;
    });
  }

}