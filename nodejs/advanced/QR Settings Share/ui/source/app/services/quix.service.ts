import {Injectable} from '@angular/core';
import {Observable, Subject} from "rxjs";
import {HttpClient, HttpHeaders} from "@angular/common/http";

@Injectable({
    providedIn: 'root'
})
export class QuixService {

    /*WORKING LOCALLY? UPDATE THESE!*/
    // NOTE !!! This token will expire, generate one with a customised expiry date from the tokens page
    public token: string = "{placeholder:token}";
    public workspaceId: string = "{placeholder:workspaceId}";
    readonly subdomain = "{placeholder:environment.subdomain}";
    /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

    public apiurl: string;

    public PersonalAccessTokenReceived: Subject<any> = new Subject<any>();
    public PersonalAccessTokenCreationError: Subject<any> = new Subject<any>();

    constructor(private httpClient: HttpClient) {

        if(this.apiurl == undefined) {
            this.apiurl = window.location.href + "api/";
        }
        console.log("API URL set to : " + this.apiurl);
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

    PushSettings(key, value, expiry, callback) {
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