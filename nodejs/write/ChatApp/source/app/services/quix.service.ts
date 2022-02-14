import { Injectable } from '@angular/core';
import {Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {HubConnection, HubConnectionBuilder, IHttpConnectionOptions} from "@microsoft/signalr";
import {map} from "rxjs/operators";
import {ParameterData} from "../models/parameter-data";
import {MessagePayload} from "../components/webchat/webchat.component";

@Injectable({
  providedIn: 'root'
})
export class QuixService {

  readonly workspace = "{placeholder:workspaceId}";
  readonly subdomain = "{placeholder:environment.subdomain}";


  private token = '{placeholder:token}';
  public readerConnection: HubConnection;
  public readerConnectionPromise: Promise<void>;
  public writerConnection: HubConnection;
  public writerConnectionPromise: Promise<void>;

  constructor(private httpClient: HttpClient) {

    const options: IHttpConnectionOptions = {
      accessTokenFactory: () => this.token,
    };

    this.readerConnection = new HubConnectionBuilder()
        .withUrl(`https://reader-${this.workspace}.${this.subdomain}.quix.ai/hub`, options)
        .withAutomaticReconnect()
        .build();

    this.readerConnectionPromise = this.readerConnection.start();

    this.writerConnection = new HubConnectionBuilder()
        .withUrl(`https://writer-${this.workspace}.${this.subdomain}.quix.ai/hub`, options)
        .withAutomaticReconnect()
        .build();

    this.writerConnectionPromise = this.writerConnection.start();
  }

  public getLastMessages(room: string) : Observable<MessagePayload[]> {
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
        } ;


    return this.httpClient.post<ParameterData>(`https://telemetry-query-${this.workspace}.${this.subdomain}.quix.ai/parameters/data`, payload, {
          headers: {
            "Authorization": "bearer " + this.token
          }
        }
    ).pipe(map(rows => {

      let result : MessagePayload[] = [];
      for (let i = 0; i < rows.timestamps.length; i++){
        result.push({
          timestamp: rows.timestamps[i],
          message: rows.stringValues["chat-message"][i],
          sentiment:          rows.numericValues["sentiment"][i],
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

    await this.writerConnection.invoke("SendEventData", "0-web-chat", room, payload);
  }
}
