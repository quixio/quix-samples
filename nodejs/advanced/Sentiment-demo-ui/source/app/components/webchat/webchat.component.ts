import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {QuixService} from "../../services/quix.service";
import {ActivatedRoute, Router} from "@angular/router";
import 'chartjs-plugin-streaming';
import {ChartDataSets, ChartOptions} from "chart.js";

export  class MessagePayload{
  public name: string;
  public message?: string;
  public sentiment?: number;
  public timestamp: number;
}

@Component({
  selector: 'app-webchat',
  templateUrl: './webchat.component.html',
  styleUrls: ['./webchat.component.sass']
})
export class WebchatComponent implements OnInit {

  @ViewChild("myChart") myChart: Chart;
  datasets: ChartDataSets[] = [{
    borderColor: "#3e4f97",
    backgroundColor: "rgba(62,79,151,0.48)",
    pointBackgroundColor: "black",
    data: [],
    label: 'Chatroom sentiment',


  }];
  options: ChartOptions & any = {

    scales: {
      yAxes:[
        {
          type: "linear",
          ticks:{
            max: 1,
            min: -1
          }
        }
      ],
      xAxes: [{
        type: 'realtime',
        realtime: {
          duration: 20000,
          refresh: 1000,
          delay: 200,
          onRefresh: chart =>{
          }
        }
      }]
    }
  };

  elementType = 'url';
  value = undefined;

  rate = 0;

  @ViewChild("messagesDiv")
  messagesDiv: ElementRef;

  @ViewChild("messagesDivMobile")
  messagesDivMobile  : ElementRef;

  public readerConnected: boolean;
  public writerConnected: boolean;

  public messages: MessagePayload[] = [];

  public role: string;
  public sentiment: number;
  public room: string;
  public message: string;
  public name: string;
  public phone: string;
  public email: string;

  constructor(private quixService: QuixService,
              private route: ActivatedRoute,
              private router: Router) { }

  public async send(){
    await this.quixService.sendMessage(this.room, "Customer", this.name, this.message, this.phone, this.email);
    this.message = "";
  }

  async ngOnInit(): Promise<void> {
    this.quixService.loaded.subscribe(x => {
      console.log("got value " + x)
      if(x == true) this.Init();
    });
    //this.quixService.loaded.share
  }

  async Init(){
    this.room = this.route.snapshot.params["room"];
    this.name = this.route.snapshot.params["name"];
    this.phone = this.route.snapshot.queryParams["phone"];
    this.email = this.route.snapshot.queryParams["email"];

    this.quixService.readerConnection.onclose(e =>{
      this.readerConnected = false;
    });

    this.quixService.readerConnection.onreconnecting(e =>{
      this.readerConnected = false;
    });

    this.quixService.readerConnection.onreconnected(e =>{
      this.readerConnected = true;
    });

    this.quixService.writerConnection.onclose(e =>{
      this.writerConnected = false;
    });

    this.quixService.writerConnection.onreconnecting(e =>{
      this.writerConnected = false;
    });

    this.quixService.writerConnection.onreconnected(e =>{
      this.writerConnected = true;
    });

    this.quixService.readerConnectionPromise.then(_ => {

      this.quixService.readerConnection.on('ParameterDataReceived', (payload) => {

        let message = this.messages.find(f => f.timestamp == payload.timestamps[0] && f.name == payload.tagValues["name"]);

        let sentiment = payload.numericValues["sentiment"] ? payload.numericValues["sentiment"][0] : 0;
        let timestamp = payload.timestamps[0];

        if (!message){
          this.messages.push({
            timestamp: timestamp,
            name: payload.tagValues["name"],
            sentiment: sentiment,
          });
        }
        else{
          message.sentiment = sentiment;
        }

        if (payload.numericValues["average_sentiment"]) {
          this.sentiment = payload.numericValues["average_sentiment"][0];

          let row = {
            x: Date.now(),
            y: this.sentiment
          }

          this.datasets[0].data.push(row as any)
        }

        setTimeout(() => this.messagesDiv.nativeElement.scrollTop = this.messagesDiv.nativeElement.scrollHeight, 200);
        setTimeout(() => this.messagesDivMobile.nativeElement.scrollTop = this.messagesDivMobile.nativeElement.scrollHeight, 200);
      });

      this.quixService.readerConnection.on('EventDataReceived', (payload) => {
        let message = this.messages.find(f => f.timestamp == payload.timestamp && f.name == payload.tags["name"]);

        let chatMessage = payload.value;
        let timestamp = payload.timestamp;

        if (!message){
          this.messages.push({
            timestamp: timestamp,
            name: payload.tags["name"],
            message: chatMessage
          });
        }

        if (payload.numericValues !== undefined && payload.numericValues["average_sentiment"]) {
          this.sentiment = payload.numericValues["average_sentiment"][0];

          let row = {
            x: Date.now(),
            y: this.sentiment
          }

          this.datasets[0].data.push(row as any)
        }

        setTimeout(() => this.messagesDiv.nativeElement.scrollTop = this.messagesDiv.nativeElement.scrollHeight, 200);
        setTimeout(() => this.messagesDivMobile.nativeElement.scrollTop = this.messagesDivMobile.nativeElement.scrollHeight, 200);
      });
      this.connect();

      this.readerConnected = true;

    }).catch(e => {
      console.log(e);
    });

    await this.quixService.writerConnectionPromise;
    this.writerConnected = true;
  }

  connect() {

    this.quixService.readerConnection.invoke('SubscribeToEvent', this.quixService.messagesTopic, this.room, 'chat-message');
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room + "-output", 'sentiment');
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room + "-output", 'chat-message');
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room + "-output", 'average_sentiment');

    let host = window.location.host;
    this.value = `${window.location.protocol}//${host}/lobby?room=${this.room}`;

    this.quixService.getLastMessages(this.room).subscribe(res => {
      this.messages = res.slice(Math.max(0, res.length - 20), res.length);
      setTimeout(() => this.messagesDiv.nativeElement.scrollTop = this.messagesDiv.nativeElement.scrollHeight, 200);
      setTimeout(() => this.messagesDivMobile.nativeElement.scrollTop = this.messagesDivMobile.nativeElement.scrollHeight, 200);
    });
  }

  public getDateFromEpoch(epoch: number){
    return new Date(epoch / 1000000)
  }
}