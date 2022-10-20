import {Injectable} from '@angular/core';
import {BehaviorSubject, combineLatest, Observable, Subject} from "rxjs";
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {HubConnection, HubConnectionBuilder, IHttpConnectionOptions} from "@microsoft/signalr";
import {map} from "rxjs/operators";
import {ParameterData} from "../models/parameter-data";
import {MessagePayload} from "../components/webchat/webchat.component";

@Injectable({
    providedIn: 'root'
})
export class QuixService {

    /*WORKING LOCALLY? UPDATE THESE!*/
    private token: string = "{placeholder:token}";
    public workspaceId: string = "{placeholder:workspaceId}";
    public messagesTopic: string = ""; //get topic ID from the Topics page
    public sentimentTopic: string = ""; //get topic ID from the Topics page
    /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

    readonly subdomain = "{placeholder:environment.subdomain}"; 
    readonly server = "" // leave blank

    public readerConnection: HubConnection;
    public readerConnectionPromise: Promise<void>;
    public writerConnection: HubConnection;
    public writerConnectionPromise: Promise<void>;
    public loaded: BehaviorSubject<any> = new BehaviorSubject<any>(false);

    constructor(
        private httpClient: HttpClient) {

        const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
        let messagesTopic$ = this.httpClient.get(this.server + "messages_topic", {headers, responseType: 'text'});
        let sentimentTopic$ = this.httpClient.get(this.server + "sentiment_topic", {headers, responseType: 'text'});

        let value$ = combineLatest(
            messagesTopic$,
            sentimentTopic$,
        ).pipe(map(([messagesTopic, sentimentTopic])=>{
            return {messagesTopic, sentimentTopic};
        }));

        value$.subscribe(vals => {
            this.messagesTopic = (this.workspaceId + "-" + vals.messagesTopic).replace("\n", "");
            this.sentimentTopic = (this.workspaceId + "-" + vals.sentimentTopic).replace("\n", "");

            this.ConnectToQuix(this.workspaceId);
        });
    }

    private ConnectToQuix(workspaceId){

        const options: IHttpConnectionOptions = {
            accessTokenFactory: () => this.token,
        };

        this.readerConnection = new HubConnectionBuilder()
            .withUrl(`https://reader-${workspaceId}.${this.subdomain}.quix.ai/hub`, options)
            .withAutomaticReconnect()
            .build();

        this.readerConnectionPromise = this.readerConnection.start();

        this.writerConnection = new HubConnectionBuilder()
            .withUrl(`https://writer-${workspaceId}.${this.subdomain}.quix.ai/hub`, options)
            .withAutomaticReconnect()
            .build();

        this.loaded.next(true);
		console.log("CONNECTED TO QUIX....");
		
        this.writerConnectionPromise = this.writerConnection.start();
    }

    public getLastMessages(room: string): Observable<MessagePayload[]> {

        let payload =
            {
                'numericParameters': [
                    {
                        'parameterName': 'sentiment',
                        'aggregationType': 'None'
                    },
                    {
                        'parameterName': 'average_sentiment',
                        'aggregationType': 'None'
                    }
                ],
                'stringParameters': [
                    {
                        'parameterName': 'chat-message',
                        'aggregationType': 'None'
                    }
                ],

                "streamIds": [
                    room + "-output"
                ],
                "groupBy": [
                    "role",
                    "name"
                ],
            };

        return this.httpClient.post<ParameterData>(`https://telemetry-query-${this.workspaceId}.${this.subdomain}.quix.ai/parameters/data`, payload, {
                headers: {
                    "Authorization": "bearer " + this.token
                }
            }
        ).pipe(map(rows => {

            let result: MessagePayload[] = [];
            for (let i = 0; i < rows.timestamps.length; i++) {
                result.push({
                    timestamp: rows.timestamps[i],
                    message: rows.stringValues["chat-message"][i],
                    sentiment: rows.numericValues["sentiment"][i],
                    name: rows.tagValues["name"][i]
                });
            }
            return result;
        }));
    }

    public async sendMessage(room: string, role: string, name: string, message: string, phone: string, email: string) {
        let payload = [
            {
                "timestamp": new Date().getTime() * 1000000,
                "tags": {
                    "room": room,
                    "role": role,
                    "name": name,
                    "phone": phone,
                    "email": email
                },
                "id": "chat-message",
                "value": message
            }
        ];

        await this.writerConnection.invoke("SendEventData", this.messagesTopic, room, payload);
    }
}