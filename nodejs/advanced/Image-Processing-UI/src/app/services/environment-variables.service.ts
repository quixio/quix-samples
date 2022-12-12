import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {combineLatest, of, Subject} from "rxjs";
import {ActivatedRoute} from "@angular/router";
import {map} from "rxjs/operators";
import {ReadyModel} from "../models/readyModel";

@Injectable({
  providedIn: 'root'
})
export class EnvironmentVariablesService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  private workingLocally = false; // set to true if working locally
  private token: string = ""; // Create a token in the Tokens menu and paste it here
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  public topic: string = ''; // get topic name from the Topics page
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  public ready: Subject<ReadyModel> = new Subject<ReadyModel>();

  // leave these blank.
  domain = "";
  server = "";
  constructor(private httpClient: HttpClient,
              private route: ActivatedRoute) {

    if(this.workingLocally){
      this.topic = this.workspaceId + '-' + this.topic;
    }
    else {
      const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
      let workspaceId$ = this.httpClient.get(this.server + 'workspace_id', {headers, responseType: 'text'});
      let processedTopic$ = this.httpClient.get(this.server + 'processed_topic', {headers, responseType: 'text'});
      let token$ = this.httpClient.get(this.server + 'sdk_token', {headers, responseType: 'text'});

      let value$ = combineLatest([
        workspaceId$,
        processedTopic$,
        token$,
        this.route.url
      ]).pipe(map(([workspaceId, processedTopic, token, url]) => {
        return {workspaceId, processedTopic, token, url};
      }));

      value$.subscribe((vals) => {
        this.workspaceId = this.stripLineFeed(vals.workspaceId);
        this.topic = this.stripLineFeed(this.workspaceId + '-' + vals.processedTopic);
        this.token = vals.token.replace('\n', '');

        //determine namespace from url
        let domain = new URL(window.location.href);
        if(domain.hostname.includes("platform.quix.ai")){
          this.domain = "platform";
        }else if(domain.hostname.includes("dev.quix.ai")){
          this.domain = "dev";
        }else{
          // assume platform
          this.domain = "platform";
        }

        console.log(this.token);
        console.log(this.topic);
        console.log(this.workspaceId);
        let url = this.buildUrl(this.workspaceId);
        console.log(url);

        let model = {token: this.token, topic:this.topic, readerUrl: url}
        this.ready.next(model);
      });
    }
  }

  private stripLineFeed(s: string): string {
    return s.replace('\n', '');
  }

  // don't change this
  baseUrl = "https://reader-[WS].[DOMAIN].quix.ai/hub";

  public buildUrl(workspaceId) {
    return this.baseUrl.replace("[WS]", workspaceId).replace("[DOMAIN]", this.domain);
  }

}
