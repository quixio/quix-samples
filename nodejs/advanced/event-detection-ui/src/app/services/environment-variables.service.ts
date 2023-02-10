import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {combineLatest, Subject} from "rxjs";
import {map} from "rxjs/operators";

@Injectable({
  providedIn: 'root'
})
export class EnvironmentVariablesService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  private workingLocally = false; // set to true if working locally
  public token: string = ''; // Create a token in the Tokens menu and paste it here
  public topic: string = ''; // Create a topic in the Topic tab
  public eventTopic: string = ''; // Create a topic in the Topic tab
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  public subdomain = ''; // leave blank. determined using portal api url
  public hubUrl = ''; // leave blank. built in constructor
  private server = ''; // for debugging. leave blank
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  private domainRegex = new RegExp("^https:\\/\\/portal-api\\.([a-zA-Z]+)\\.quix\\.ai");
  public ConfigurationLoaded: Subject<any> = new Subject<any>();

  constructor(private httpClient: HttpClient) {

    if (this.workingLocally) {
      this.ConfigurationLoaded.next('');
    }
    else{

      const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
      let token$ = this.httpClient.get(this.server + "sdk_token", {headers, responseType: 'text'});
      let workspaceId$ = this.httpClient.get(this.server + "workspace_id", {headers, responseType: 'text'});
      let portalApi$ = this.httpClient.get(this.server + "portal_api", {headers, responseType: 'text'})
      let topic$ = this.httpClient.get(this.server + "topic", {headers, responseType: 'text'})
      let eventTopic$ = this.httpClient.get(this.server + "eventTopic", {headers, responseType: 'text'})

      // @ts-ignore
      let value$ = combineLatest(
          token$,
          workspaceId$,
          portalApi$,
          topic$,
          eventTopic$
      ).pipe(map(([token, workspaceId, portalApi, topic, eventTopic]: any) =>
          ({token, workspaceId, portalApi, topic, eventTopic})));

      // @ts-ignore
      value$.subscribe(vals => {
        this.token = (vals.token).replace("\n", "");
        this.workspaceId = (vals.workspaceId).replace("\n", "");
        this.topic = (vals.topic).replace("\n", "");
        this.eventTopic = (vals.eventTopic).replace("\n", "");

        let portalApi = vals.portalApi.replace("\n", "");
        let matches = portalApi.match(this.domainRegex);
        if (matches) {
          this.subdomain = matches[1];
        } else {
          this.subdomain = "platform"; // default to prod
        }

        this.hubUrl = 'https://reader-' + this.workspaceId + '.' + this.subdomain + '.quix.ai/hub'

        console.log("Token=" + this.token);
        console.log("Topic=" + this.topic);
        console.log("EventTopic=" + this.eventTopic);
        console.log("WorkspaceId=" + this.workspaceId);
        console.log("Subdomain=" + this.subdomain);
        console.log("HubUrl=" + this.hubUrl);

        this.ConfigurationLoaded.next('');
      });
    }
  }

}
