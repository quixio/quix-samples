import {Component, OnInit} from '@angular/core';
import {HubConnection, HubConnectionBuilder, IHttpConnectionOptions} from '@microsoft/signalr';
import {HttpClient} from '@angular/common/http';
import {ParameterData} from './models/parameter-data';
import {Observable} from 'rxjs';
import {Stream} from './models/stream';
import {EventValue} from "./models/eventValue";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent{
  title = 'quix-template';

}
