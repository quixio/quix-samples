import {Injectable} from '@angular/core';
import {Observable, Subject} from "rxjs";
import {HubConnection, HubConnectionBuilder, IHttpConnectionOptions} from "@microsoft/signalr";
import {PersonalAccessTokenCreatedUiNotification} from "../models/PersonalAccessTokenCreatedUiNotification";
import {HttpClient, HttpHeaders} from "@angular/common/http";

@Injectable({
    providedIn: 'root'
})
export class QuixService {

    /*WORKING LOCALLY? UPDATE THESE!*/
    public token: string = "{placeholder:token}";
    public workspaceId: string = "{placeholder:workspaceId}";
    readonly subdomain = "{placeholder:environment.subdomain}";
    /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

    public apiurl: string = "/api/";

    private hubConnection;
    public PersonalAccessTokenReceived: Subject<any> = new Subject<any>();
    public PersonalAccessTokenCreationError: Subject<any> = new Subject<any>();


    constructor(private httpClient: HttpClient) {
    }

    public createPersonalAccessToken(tokenName: string, expirationUtc: Date) {
        let token = {
            name: tokenName,
            expiresAt: expirationUtc
        };

        return this.post("portal-api", `profile/tokens`, token).subscribe(
            data => console.log("Success", data),
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

    public startHubConnection(): Observable<HubConnection> {

        let service = "portal-api-notifications";
        let hub = "/hub";
        let retryDelays: number[] = [1000, 1000, 1000];

        let options: IHttpConnectionOptions = {
            accessTokenFactory: () => this.token
        };
        this.hubConnection = new HubConnectionBuilder()
            .withUrl(`https://${service}.${this.subdomain}.quix.ai${hub}`, options)
            .withAutomaticReconnect(retryDelays)
            .build();

        return this.hubConnection.start()
            .then(() => {
                console.log("Hub started");

                this.hubConnection.on('PersonalAccessTokenCreated', (data: PersonalAccessTokenCreatedUiNotification) => {
                    this.PersonalAccessTokenReceived.next(data);
                });

            }).catch(err => {
                console.log(err);
            })
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
                    callback(JSON.stringify(url));
                }
            });
    }
}