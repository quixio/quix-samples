import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {of} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class EnvironmentVariablesService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*Create a token in the Tokens menu and paste it here*/
  Token: string = "";
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /* TO RUN LOCALLY */
  /*
  * Change UseHardcodedValues to True
  * And hardcode the values from your Quix workspace
  * */

  UseHardcodedValues = false;
  Topic: string = "";
  WorkspaceId: string = "";

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  constructor(private httpClient: HttpClient) {}

  // don't change this
  ReaderUrl: string;
  baseUrl = "https://reader-[WS].dev.quix.ai/hub";

  public buildUrl(workspaceId) {
    return this.baseUrl.replace("[WS]", workspaceId);
  }

  GetToken() {
    //if(this.UseHardcodedValues)
    return of(this.Token);

    //const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
    //return this.httpClient.get("sdk_token", {headers, responseType: 'text'});
  }

  GetTopic() {
    if(this.UseHardcodedValues)
      return of(this.Topic);

    const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
    return this.httpClient.get("processed_topic", {headers, responseType: 'text'});
  }

  GetWorkspaceId() {
    if(this.UseHardcodedValues)
      return of(this.WorkspaceId);

    const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
    return this.httpClient.get("workspace_id", {headers, responseType: 'text'});
  }
}
