import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {of} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class EnvironmentVariablesService {

  /* TO RUN LOCALLY */
  /*
  * Change UseHardcodedValues to True
  * And hardcode the values from your Quix workspace
  * */

  UseHardcodedValues = true;
  Token: string = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlpXeUJqWTgzcXotZW1pUlZDd1I4dyJ9.eyJodHRwczovL3F1aXguYWkvb3JnX2lkIjoicXVpeGRldiIsImh0dHBzOi8vcXVpeC5haS9vd25lcl9pZCI6ImF1dGgwfDM5ZGYyZTVlLTM3YjQtNDM0MS1hYjE3LWQ1YjI4MDdiOTRmMCIsImh0dHBzOi8vcXVpeC5haS90b2tlbl9pZCI6IjU0MDlkNGViLWVmNWQtNGU0MC05N2NiLTY1MDZhNjJlYjdlMyIsImh0dHBzOi8vcXVpeC5haS9leHAiOiIxNzE3NjI0ODAwIiwiaHR0cHM6Ly9xdWl4LmFpL3JvbGVzIjoiYWRtaW4iLCJpc3MiOiJodHRwczovL2F1dGguZGV2LnF1aXguYWkvIiwic3ViIjoidTl6dTIzTnBtaXFZQ29EVHRrUlEzS1o0N2VkbG5ZbXBAY2xpZW50cyIsImF1ZCI6Imh0dHBzOi8vcG9ydGFsLWFwaS5kZXYucXVpeC5haS8iLCJpYXQiOjE2NjMwNzMwNTMsImV4cCI6MTY2NTY2NTA1MywiYXpwIjoidTl6dTIzTnBtaXFZQ29EVHRrUlEzS1o0N2VkbG5ZbXAiLCJndHkiOiJjbGllbnQtY3JlZGVudGlhbHMiLCJwZXJtaXNzaW9ucyI6W119.MRNJobywNID4FEAFKVVY8GBo6R4tuceJTVxPk4RyuxHUEod6H5qGbNX6mEyUlqYsmm6N4qpBqqeeIK-OEurOognYEv4lJ-SkqEVDFZ7MVeDH4oPkPS7eZJFJbw4ZDp346xUye7ahLhlbf2PePVhihwJh4IkAQeMVLvHfRu2BnbntWZybSnWgm19Yq9H7CT2pD_Q6ebtPLQHkdzoEQ9D2J4gmIS5ZTi6aw-vaUxCPgftfisR0aDmWpX52iAhyITvwAZtjWUfcFKD1cwqJOHi8jB8o1QYCd6n6U8Sa74Bw_-9yvGpXLDbsHaKkF4o_EyPwi3EkZ_YpOADoxx3DOzci0w";
  Topic: string = "image-proccessed-merged";
  WorkspaceId: string = "quixdev-imageprocessingdemo";

  // UseHardcodedValues = false;
  // Token: string = "";
  // Topic: string = "";
  // WorkspaceId: string = "";

  // don't change this
  ReaderUrl: string;
  baseUrl = "https://reader-[WS].dev.quix.ai/hub";

  constructor(private httpClient: HttpClient) {

    console.log("Constructing Env Var Svc");

    //const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');

    if(this.UseHardcodedValues) {
      return;
    }

    // let a = this.httpClient.get("workspace_id", {headers, responseType: 'text'});
    // let b = this.httpClient.get("sdk_token", {headers, responseType: 'text'});
    // let c = this.httpClient.get("processed_topic", {headers, responseType: 'text'});
    //
    // forkJoin({a,b,c}).subscribe(x => console.log(x));
    //
    // Promise.all([a, b, c]).then((values)=>{
    //   values[0].subscribe(s=>this.WorkspaceId = s);
    //   values[1].subscribe(s=>this.Token = s);
    //   values[2].subscribe(s=>this.Topic = s);
    // });

    //this.ReaderUrl = this.buildUrl();
    //console.log("URL IS:");
    //console.log(this.ReaderUrl);
  }

  public buildUrl(workspaceId) {
    return this.baseUrl.replace("[WS]", workspaceId);
  }

  // public Thing1(): Observable<string>{
  //   const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
  //   headers.set('Access-Control-Allow-Origin', '*');
  //   return this.httpClient.get("https://cors-anywhere.herokuapp.com/https://names.drycodes.com/1", {headers, responseType: 'text'});
  // }
  //
  // public Thing2(): Observable<string>{
  //   const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
  //   headers.set('Access-Control-Allow-Origin', '**');
  //
  //   return this.httpClient.get("https://cors-anywhere.herokuapp.com/https://names.drycodes.com/1", {headers, responseType: 'text'});
  // }

  GetToken() {
    if(this.UseHardcodedValues)
      return of(this.Token);

    const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
    return this.httpClient.get("sdk_token", {headers, responseType: 'text'});
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
