import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { HubConnection, HubConnectionBuilder, IHttpConnectionOptions } from '@microsoft/signalr';
import { BehaviorSubject, combineLatest, Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { MessagePayload } from '../models/messagePayload';
import { ParameterData } from '../models/parameterData';

@Injectable({
  providedIn: 'root'
})
export class QuixService {

  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/
  /*WORKING LOCALLY? UPDATE THESE!*/
  private workingLocally = false; // set to true if working locally
  private token: string = ""; // Create a token in the Tokens menu and paste it here
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
  public messagesTopic: string = ''; // get topic name from the Topics page
  public sentimentTopic: string = ''; // get topic name from the Topics page
  /*~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-*/

  readonly subdomain = 'platform'; // leave as 'platform'
  readonly server = ''; // leave blank

  public readerConnection: HubConnection;
  public readerConnectionPromise: Promise<void>;
  public writerConnection: HubConnection;
  public writerConnectionPromise: Promise<void>;
  public loaded: BehaviorSubject<any> = new BehaviorSubject<any>(false);

  constructor(private httpClient: HttpClient) {

    if(this.workingLocally){
      this.messagesTopic = this.workspaceId + '-' + this.messagesTopic;
      this.sentimentTopic = this.workspaceId + '-' + this.sentimentTopic;
      this.ConnectToQuix(this.workspaceId);
    }
    else {
      const headers = new HttpHeaders().set('Content-Type', 'text/plain; charset=utf-8');
      let workspaceId$ = this.httpClient.get(this.server + 'workspace_id', {headers, responseType: 'text'});
      let messagesTopic$ = this.httpClient.get(this.server + 'messages_topic', {headers, responseType: 'text'});
      let sentimentTopic$ = this.httpClient.get(this.server + 'sentiment_topic', {headers, responseType: 'text'});
      let token$ = this.httpClient.get(this.server + 'sdk_token', {headers, responseType: 'text'});

      let value$ = combineLatest([
        workspaceId$,
        messagesTopic$,
        sentimentTopic$,
        token$
      ]).pipe(map(([workspaceId, messagesTopic, sentimentTopic, token]) => {
        return {workspaceId, messagesTopic, sentimentTopic, token};
      }));

      value$.subscribe((vals) => {
        this.workspaceId = this.stripLineFeed(vals.workspaceId);
        this.messagesTopic = this.stripLineFeed(this.workspaceId + '-' + vals.messagesTopic);
        this.sentimentTopic = this.stripLineFeed(this.workspaceId + '-' + vals.sentimentTopic);
        this.token = vals.token.replace('\n', '');
        this.ConnectToQuix(this.workspaceId);
      });
    }
  }

  private stripLineFeed(s: string): string {
    return s.replace('\n', '');
  }

  private ConnectToQuix(workspaceId: string): void {

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
    console.log('CONNECTED TO QUIX....');

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

      'streamIds': [
        room + '-output'
      ],
      'groupBy': [
        'role',
        'name'
      ],
    };

    return this.httpClient.post<ParameterData>(
      `https://telemetry-query-${this.workspaceId}.${this.subdomain}.quix.ai/parameters/data`,
      payload,
      {
        headers: { 'Authorization': 'bearer ' + this.token }
      }
    ).pipe(map(rows => {
      let result: MessagePayload[] = [];
      rows.timestamps.forEach((timestamp, i) => {
        result.push({
          timestamp,
          value: rows.stringValues['chat-message'][i],
          sentiment: rows.numericValues['sentiment'][i],
          name: rows.tagValues['name'][i]
        });
      })
      return result;
    }));
  }

  public async sendMessage(room: string, role: string, name: string, message: string, phone: string, email: string) {
    let payload =
        {
          'timestamps': [new Date().getTime() * 1000000],
          'tagValues': {
            'room': [room],
            'role': [role],
            'name': [name],
            'phone': [phone],
            'email': [email]
          },
          'stringValues': {
            'chat-message': [message]
          }
        };

    try {

    await this.writerConnection.invoke('SendParameterData', this.messagesTopic, room, payload);
  } catch (e) {
        console.log(e);
    }
  }
}
