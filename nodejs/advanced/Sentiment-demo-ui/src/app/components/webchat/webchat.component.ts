import { Component, ElementRef, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { NgxQrcodeElementTypes, NgxQrcodeErrorCorrectionLevels } from '@techiediaries/ngx-qrcode';
import { Chart, ChartDataset, ChartOptions, Legend, LinearScale, LineController, LineElement, PointElement } from 'chart.js';
import 'chartjs-adapter-luxon';
import ChartStreaming, { RealTimeScale } from 'chartjs-plugin-streaming';
import { filter, take } from 'rxjs';
import { EventData } from 'src/app/models/eventData';
import { MessagePayload } from 'src/app/models/messagePayload';
import { ParameterData } from 'src/app/models/parameterData';
import { QuixService } from '../../services/quix.service';

@Component({
  selector: 'app-webchat',
  templateUrl: './webchat.component.html',
  styleUrls: ['./webchat.component.scss']
})
export class WebchatComponent implements OnInit, OnDestroy {
  @ViewChild('chatWrapper') chatWrapper: ElementRef<HTMLElement>;
  @ViewChild('myChart') myChart: Chart;

  readerConnected: boolean;
  writerConnected: boolean;

  ngxQrcodeElementTypes = NgxQrcodeElementTypes;
  ngxQrcodeErrorCorrectionLevels = NgxQrcodeErrorCorrectionLevels
  qrValue: string;

  messages: MessagePayload[] = [];

  room: string;
  name: string;
  phone: string;
  email: string;

  chatForm = new FormGroup({
    message: new FormControl('')
  });

  datasets: ChartDataset[] = [{
    data: [],
    label: 'Chatroom sentiment',
    borderColor: '#0064ff',
    backgroundColor: 'rgba(0, 100, 255, 0.24)',
    pointBackgroundColor: 'white',
    pointBorderColor: 'black',
    pointBorderWidth: 2,
    fill: true
  }];

  options: ChartOptions = {
    interaction: {
      mode: 'index',
      intersect: false
    },
    maintainAspectRatio: false,
    animation: false,
    scales: {
      y: {
        type: 'linear',
        max: 1,
        min: -1
      },
      x: {
        type: 'realtime',
        realtime: {
          duration: 20000,
          refresh: 1000,
          delay: 200,
          onRefresh: (chart: Chart) => {
          }
        }
      }
    },
    plugins: {
      legend: {
        display: false
      }
    }
  };

  constructor(private quixService: QuixService, private route: ActivatedRoute) {
    Chart.register(
      LinearScale,
      LineController,
      PointElement,
      LineElement,
      RealTimeScale,
      Legend,
      ChartStreaming
    );
  }

  public async send() {
    const message: string = this.chatForm.controls.message.value || '';
    await this.quixService.sendMessage(this.room, 'Customer', this.name, message, this.phone, this.email);
    this.chatForm.reset();
  }

  async ngOnInit(): Promise<void> {
    this.quixService.loaded.pipe(filter(f => !!f), take(1)).subscribe(() => this.init());
  }

  async init() {
    const paramMap = this.route.snapshot.paramMap;
    this.room = paramMap.get('room') || '';
    this.name = paramMap.get('name') || '';
    this.phone = paramMap.get('phone') || '';
    this.email = paramMap.get('email') || '';

    this.quixService.readerConnection.onclose(e => {
      this.readerConnected = false;
    });

    this.quixService.readerConnection.onreconnecting(e => {
      this.readerConnected = false;
    });

    this.quixService.readerConnection.onreconnected(e => {
      this.readerConnected = true;
    });

    this.quixService.writerConnection.onclose(e => {
      this.writerConnected = false;
    });

    this.quixService.writerConnection.onreconnecting(e => {
      this.writerConnected = false;
    });

    this.quixService.writerConnection.onreconnected(e => {
      this.writerConnected = true;
    });

    this.quixService.readerConnectionPromise.then(_ => {

      this.quixService.readerConnection.on('ParameterDataReceived', (payload: ParameterData) => {
        let timestamp = payload.timestamps[0];
        let name = payload.tagValues['name'][0]
        let sentiment = payload.numericValues['sentiment'] ? payload.numericValues['sentiment'][0] : 0;
        let averageSentiment = payload.numericValues['average_sentiment'] ? payload.numericValues['average_sentiment'][0] : 0;
        let message = this.messages.find(f => f.timestamp === timestamp && f.name === payload.tagValues['name'][0]);

        if (!message) {
          this.messages.push({ timestamp, name, sentiment, value: payload.stringValues["chat-message"][0]});
        } else {
          message.sentiment = sentiment;
          message.value = payload.stringValues["chat-message"][0]
        }

        if (averageSentiment) {
          let row = { x: timestamp / 1000000, y: averageSentiment }
          this.datasets[0].data.push(row as any)
        }

        const el = this.chatWrapper.nativeElement;
        const isScrollToBottom = el.offsetHeight + el.scrollTop >= el.scrollHeight;

        if (isScrollToBottom) setTimeout(() => el.scrollTop = el.scrollHeight);
      });


      this.connect();
      this.readerConnected = true;
    }).catch(e => console.log(e));

    await this.quixService.writerConnectionPromise;
    this.writerConnected = true;
  }

  connect() {
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.messagesTopic, this.room, 'chat-message');

    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room, 'sentiment');
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room, 'chat-message');
    this.quixService.readerConnection.invoke('SubscribeToParameter', this.quixService.sentimentTopic, this.room, 'average_sentiment');

    let host = window.location.host;
    this.qrValue = `${window.location.protocol}//${host}/lobby?room=${this.room}`;

    this.quixService.getLastMessages(this.room).subscribe(lastMessage => {
      this.messages = lastMessage.slice(Math.max(0, lastMessage.length - 20), lastMessage.length);

      const el = this.chatWrapper.nativeElement;
      setTimeout(() => el.scrollTop = el.scrollHeight);
    });
  }

  getDateFromTimestamp(timestamp: number) {
    return new Date(timestamp / 1000000)
  }

  ngOnDestroy(): void {
    this.quixService.readerConnection.invoke('UnsubscribeFromParameter', this.quixService.messagesTopic, this.room, 'chat-message');
    this.quixService.readerConnection.invoke('UnsubscribeFromParameter', this.quixService.sentimentTopic, this.room, 'sentiment');
    this.quixService.readerConnection.invoke('UnsubscribeFromParameter', this.quixService.sentimentTopic, this.room, 'chat-message');
    this.quixService.readerConnection.invoke('UnsubscribeFromParameter', this.quixService.sentimentTopic, this.room, 'average_sentiment');
  }
}
