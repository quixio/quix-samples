import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {QuixService} from "../../services/quix.service";
import {ActivatedRoute, Router} from "@angular/router";
import 'chartjs-plugin-streaming';
import {ChartDataSets, ChartOptions} from "chart.js";

export  class MessagePayload{
  public name: string;
  public message: string;
  public sentiment: number;
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

  public connected: boolean;

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

    console.log("Sent");

    this.message = "";
  }

  ngOnInit(): void {

    this.room = this.route.snapshot.params["room"];
    this.name = this.route.snapshot.params["name"];
    this.phone = this.route.snapshot.params["phone"];
    this.email = this.route.snapshot.params["email"];

    this.quixService.connection.onclose(e =>{
      this.connected = false;
    });


    this.quixService.connection.onreconnecting(e =>{
      this.connected = false;
    });


    this.quixService.connection.onreconnected(e =>{
      this.connected = true;
    });

    this.quixService.connectionPromise.then(_ => {

      this.quixService.connection.on('ParameterDataReceived', (payload) => {


        let chatMessage = payload.stringValues["chat-message"][0];
        let sentiment = payload.numericValues["sentiment"] ? payload.numericValues["sentiment"][0] : 0;
        let timestamp = payload.timestamps[0];

        this.messages.push({
          timestamp: timestamp,
          name: payload.tagValues["name"],
          sentiment:sentiment,
          message: chatMessage
        });

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
      this.connect();

    }).catch(e => {
      console.log(e);
    });
  }

  connect() {
    this.quixService.connection.invoke('SubscribeToParameter', '{placeholder:broadcast}', this.room + "-output", 'sentiment');
    this.quixService.connection.invoke('SubscribeToParameter', '{placeholder:broadcast}', this.room + "-output", 'chat-message');
    this.quixService.connection.invoke('SubscribeToParameter', '{placeholder:broadcast}', this.room + "-output", 'average_sentiment');
    this.connected = true;

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
