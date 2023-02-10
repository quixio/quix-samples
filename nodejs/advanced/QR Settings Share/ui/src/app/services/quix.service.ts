import {Injectable} from '@angular/core';
import {combineLatest, Observable, Subject} from "rxjs";
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {map} from "rxjs/operators";

@Injectable({
    providedIn: 'root'
})
export class QuixService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  private workingLocally = false; // set to true if working locally
  private token: string = ''; // Create a token in the Tokens menu and paste it here
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  public subdomain = '';
  public apiurl = ''; // leave as is

  private domainRegex = new RegExp("^https:\\/\\/portal-api\\.([a-zA-Z]+)\\.quix\\.ai");

  public PersonalAccessTokenReceived: Subject<any> = new Subject<any>();
  public PersonalAccessTokenCreationError: Subject<any> = new Subject<any>();

  constructor(private httpClient: HttpClient) {

    if (!this.workingLocally) {

      if (this.apiurl === '') {
        this.apiurl = window.location.href + "api/";
      }
      console.log("API URL set to : " + this.apiurl);

      const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
      let bearerToken$ = this.httpClient.get(this.apiurl + "bearer_token", {headers, responseType: 'text'});
      let workspaceId$ = this.httpClient.get(this.apiurl + "workspace_id", {headers, responseType: 'text'});
      let portalApi$ = this.httpClient.get(this.apiurl + "portal_api", {headers, responseType: 'text'})

      // @ts-ignore
      let value$ = combineLatest(
          bearerToken$,
          workspaceId$,
          portalApi$
      ).pipe(map(([bearerToken, workspaceId, portalApi]: any) => ({bearerToken, workspaceId, portalApi})));

      value$.subscribe(vals => {
        this.token = (vals.bearerToken).replace("\n", "");
        this.workspaceId = (vals.workspaceId).replace("\n", "");

        let portalApi = vals.portalApi.replace("\n", "");
        let matches = portalApi.match(this.domainRegex);
        if (matches) {
          this.subdomain = matches[1];
        } else {
          this.subdomain = "platform"; // default to prod
        }

        console.log("Token=" + this.token);
        console.log("workspaceId=" + this.workspaceId);
        console.log("Subdomain=" + this.subdomain);
      });
    }
  }

  public createPersonalAccessToken(tokenName: string, expirationUtc: Date) {
    let token = {
      name: tokenName,
      expiresAt: expirationUtc
    };

    return this.post("portal-api", `profile/tokens`, token).subscribe(
        data => {
          this.PersonalAccessTokenReceived.next(data);
        },
        error => {
          this.PersonalAccessTokenCreationError.next(error);
          console.log("Error", error)
        }
    );
  }

  public post<T>(service: string, path: string, body: any, header?: any, withCredentials?: boolean): Observable<T> {
    let domain = this.subdomain + ".quix.ai";

    let requestHeader = {
      Authorization: "bearer " + this.token,
      ...header
    };

    let requestOptions = {
      headers: requestHeader,
      withCredentials: withCredentials
    };

    let url: string = `https://${service}.${domain}/${path}`;
    return this.httpClient.post<T>(url, body, requestOptions);
  }

  pushSettings(key: string, value: any, expiry: number, callback: any) {
    let item = {
      'key': key,
      'expiry': expiry,
      'value': value
    };

    const headers = new HttpHeaders().set('Content-Type', 'application/json');

    this.httpClient.post(this.apiurl, item, {headers, responseType: "blob", observe: "response"})
        .subscribe(data => {
          if (data.status === 200) {
            let url = this.apiurl + key;
            callback(url);
          }
        });
  }
}