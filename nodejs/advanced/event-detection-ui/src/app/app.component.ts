import { AgmInfoWindow } from '@agm/core';
import { Component, ElementRef, OnInit, QueryList, ViewChild, ViewChildren } from '@angular/core';
import { FormControl } from '@angular/forms';
import { MatDialog, MatDialogRef, MatDialogState } from '@angular/material/dialog';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HubConnectionBuilder } from '@microsoft/signalr';
import { Chart, ChartConfiguration, ChartDataset, ChartOptions, Legend, LinearScale, LineController, LineElement, PointElement } from 'chart.js';
import 'chartjs-adapter-luxon';
import ChartStreaming, { RealTimeScale } from 'chartjs-plugin-streaming';
import { Subject, take } from 'rxjs';
import { AlertComponent } from './components/alert/alert.component';
import { AlertsDialogComponent } from './components/alerts-dialog/alerts-dialog.component';
import { Alert } from './models/alert';
import { EventData } from './models/eventData';
import { ParameterData } from './models/parameterData';
import { bufferThrottleTime } from './models/utils';
import { Position, Vehicle } from './models/vehicle';
import { EnvironmentVariablesService } from './services/environment-variables.service';
import { UserService } from './services/user.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  @ViewChild('canvas', { static: true }) canvas: ElementRef<HTMLCanvasElement>;
  @ViewChildren('infoWindow') infoWindows: QueryList<AgmInfoWindow>;
  @ViewChild('tableCell', { static: true }) tableCell: ElementRef<HTMLDivElement>;

  chart: Chart;
  datasets: ChartDataset[] = [];
  currentDelay: number;
  options: ChartOptions = {
    interaction: {
      mode: 'index',
      intersect: false
    },
    maintainAspectRatio: false,
    animation: false,
    scales: {
      x: {
        type: 'realtime',
        realtime: {
          duration: 20000,
          refresh: 500,
        }
      }
    },
    plugins: {
      legend: {
        position: 'top',
        align: 'start',
        labels: {
          filter: (item) => item.text !== 'crash',
          usePointStyle: true,
          boxHeight: 7,
          padding: 15,
          color: '#000',
          font: {
            weight: 'bold',
            size: 12
          }
        }
      },
      tooltip: {
        usePointStyle: true,
        backgroundColor: '#fff',
        bodyColor: '#646471',
        titleColor: '#000',
        borderColor: Chart.defaults.borderColor.toString(),
        borderWidth: 1,
        filter: (item) => item.dataset.label !== 'crash',
      }
    }
  };
  configuration: ChartConfiguration = {
    type: 'line',
    data: {
      datasets: this.datasets
    },
    options: this.options
  }

  chartParameters = ['gForceX', 'gForceY', 'gForceZ', 'crash'];
  chartColors = ['#008eff', '#ca5fff', '#fe9353', '#ff4040']
  vehicles = new Map<string, Vehicle>();
  vehicleControl = new FormControl()
  unreadAlertsCount: number = 0;
  alerts: Alert[] = [];
  dialogRef: MatDialogRef<AlertsDialogComponent>;
  markerImg: HTMLImageElement;
  selectedIndex: number | undefined;
  connected: boolean;
  reconnecting: boolean;
  dataSource: EventData[] = [];
  dataSourceChange = new Subject<EventData>();
  scroll: { height: number, top: number };

  get selectedPosition(): Position | undefined {
    if (this.selectedIndex === undefined) return;
    return this.vehicles.get(this.vehicleControl.value)?.alerts?.position[this.selectedIndex]
  }

  constructor(
    private environmentVariablesService: EnvironmentVariablesService,
    private snackBar: MatSnackBar,
    private userService: UserService,
    private matDialog: MatDialog,
  ) {
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

  openSnackBar(alert: Alert) {
    if (this.dialogRef?.getState() === MatDialogState.OPEN) {
      this.dialogRef.componentInstance.alerts = this.alerts;
      this.dialogRef.componentInstance.unreadAlertsCount = this.unreadAlertsCount;
      return;
    };

    const component = AlertComponent;
    this.snackBar.openFromComponent(component, {
      duration: 3000,
      horizontalPosition: 'end',
      verticalPosition: 'top',
      panelClass: 'snackbar-alert',
      data: {
        preClose: () => { this.snackBar.dismiss() },
        alert
      }
    });
  }

  openDialog(): void {
    this.snackBar.dismiss();
    this.dialogRef = this.matDialog.open(AlertsDialogComponent, {
      width: '400px',
      maxWidth: '100%',
      height: '100%',
      backdropClass: '_side-dialog-backdrop',
      panelClass: '_side-dialog-panel',
      enterAnimationDuration: '0ms',
      exitAnimationDuration: '0ms',
      data: {
        alerts: this.alerts,
        unreadAlertsCount: this.unreadAlertsCount
      }
    });

    this.dialogRef.afterClosed().pipe(take(1)).subscribe(() => this.unreadAlertsCount = 0);
  }

  ngOnInit(): void {

    const ctx = this.canvas.nativeElement.getContext('2d');
    this.chart = new Chart(ctx!, this.configuration);

    this.userService.streamId$.subscribe((streamId: string) => {
      this.vehicleControl.setValue(streamId);
    });

    this.markerImg = this.generateSVGForPoint()

    this.environmentVariablesService.ConfigurationLoaded.subscribe(_=>{
      let token = this.environmentVariablesService.token;
      let dataTopic = this.environmentVariablesService.topic;
      let eventTopic = this.environmentVariablesService.eventTopic;
      let hubUrl = this.environmentVariablesService.hubUrl;

      const options = { accessTokenFactory: () => token };
      const connection = new HubConnectionBuilder()
          .withAutomaticReconnect()
          .withUrl(hubUrl, options)
          .build();
      connection.onreconnecting(e => {
        this.connected = false;
        this.reconnecting = true;
      });
      connection.onreconnected(e => {
        this.connected = true;
        this.reconnecting = false;
      });
      connection.onclose(e => {
        this.connected = false;
        this.reconnecting = false;
      });
      connection.start().then(() => {
        console.log('SignalR connected.');
        this.connected = true;
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Speed');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Latitude');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Longitude');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Altitude');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Accuracy');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'Heading');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'gForceX');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'gForceY');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'gForceZ');
        connection.invoke('SubscribeToParameter', dataTopic, '*', 'BatteryLevel');
        connection.invoke('SubscribeToParameter', eventTopic, '*', 'shaking');
        connection.invoke('SubscribeToEvent', eventTopic, '*', 'crash');
      });

      connection.on('EventDataReceived', (data: EventData) => {
        if (this.chartParameters.includes(data.id)) {
          this.updateChart(data.id, { x: data.timestamp / 1000000, y: 1 }, true)
        }

        const alert: Alert = {
          title: data.value,
          streamId: data.streamId,
          timestamp: data.timestamp,
          color: 'warn',
          icon: 'warning'
        };

        this.unreadAlertsCount++;
        this.alerts.push(alert);
        this.openSnackBar(alert);

        const vehicle: Vehicle = this.vehicles.get(data.streamId) || {};
        const position: Position = { latitude: vehicle.latitude || 0, longitude: vehicle.longitude || 0, };

        if (!vehicle.alerts) vehicle.alerts = { data: [], position: [] } ;
        vehicle.alerts.data = [...vehicle.alerts.data, data];
        vehicle.alerts.position = [...vehicle.alerts.position, position]
        this.vehicles.set(data.streamId, vehicle);

        this.dataSourceChange.next(data);
      });

      connection.on('ParameterDataReceived', (data: ParameterData) => {
        if (!this.vehicleControl.value) this.vehicleControl.setValue(data.streamId);

        const vehicle: Vehicle = this.vehicles.get(data.streamId) || {};
        data.timestamps.forEach((timestamp, i) => {
          vehicle.name = data.streamId;

          Object.keys(data.numericValues).forEach((key) => {
            if (this.chartParameters.includes(key)) {
              this.updateChart(key, { x: timestamp / 1000000, y: data.numericValues[key][i] })
            }
          });

          if (data.numericValues['BatteryLevel']) vehicle.batteryLevel = data.numericValues['BatteryLevel'][i] * 100;
          if (data.numericValues['Accuracy']) vehicle.accuracy = data.numericValues['Accuracy'][i];
          if (data.numericValues['Heading']) vehicle.heading = data.numericValues['Heading'][i];
          if (data.numericValues['Accuracy'] && data.numericValues['Accuracy'][i] > 0 && data.numericValues['Accuracy'][i] < 100) {
            if (data.numericValues['Latitude']) vehicle.latitude = data.numericValues['Latitude'][i];
            if (data.numericValues['Longitude']) vehicle.longitude = data.numericValues['Longitude'][i];
            if (data.numericValues['Altitude']) vehicle.altitude = data.numericValues['Altitude'][i];
            if (data.numericValues['Speed']) vehicle.speed = data.numericValues['Speed'][i];
            if (vehicle.latitude && vehicle.longitude) {
              vehicle.tail = [...(vehicle.tail || []), { lat: vehicle.latitude, lng: vehicle.longitude }]
              vehicle.lastPosition = new Date(timestamp / 1000000);
            }
          }
        });
        this.vehicles.set(data.streamId, vehicle);
      });

      this.dataSourceChange.pipe(bufferThrottleTime<EventData>(500)).subscribe((data) => {
        this.dataSource = [ ...this.dataSource, ...data];
      });
    });
  }

  updateScroll(): void {
    if (this.tableCell.nativeElement.scrollTop > 0) {
      const height = this.tableCell.nativeElement.scrollHeight - this.scroll.height;
      this.tableCell.nativeElement.scrollTop += height;
    }

    this.scroll = {
      height: this.tableCell.nativeElement.scrollHeight,
      top: this.tableCell.nativeElement.scrollTop
    }
  }

  updateChart(key: string, point: { x: number, y: number }, isEvent: boolean = false): void {
    const delay = Date.now() - point.x;
    const offset = 1000;
    if (!this.currentDelay || this.currentDelay - delay > offset || this.currentDelay - delay < -offset) {
      (this.options!.scales!['x'] as any).realtime.delay = delay + offset;
      this.currentDelay = delay;
    }

    let dataset = this.datasets.find((f) => f.label === key);
    if (dataset) {
      dataset.data.push(point);
    } else {
      const color = this.chartColors[this.chartParameters.indexOf(key)];
      let options: any = { type: 'linear', axis: 'y', display: false };
      let dataset: ChartDataset<'line'> = {
        data: [point],
        label: key,
        yAxisID: key,
        borderColor: color,
        pointBackgroundColor: color,
        pointHoverBorderWidth: 0,
        pointRadius: 0
      };

      if (isEvent) {
        const image = new Image();
        image.src = 'assets/alert.png'
        dataset = { ...dataset, pointStyle: image, pointRadius: 10, showLine: false, order: -1 };
        options = { ...options, min: 0.9, max: 2 }
      }

      this.options.scales![key] = options;
      this.datasets.push(dataset);
      this.chart?.update();
    }
  }

  generateSVGForPoint(): HTMLImageElement {
    const svgString = this.getSvgString(this.chartColors[0]);
    const svgUrl = URL.createObjectURL(new Blob([svgString], { type: 'image/svg+xml' }));;

    // If they don't already exist then we can generate the SVG blob url and then add
    // it to the map cache for later use
    const image = new Image();
    image.src = svgUrl;
    return image;
  }

  getSvgString(color: string): string {
    return `
		<svg width="40" height="41" viewBox="0 0 40 41" fill="none" xmlns="http://www.w3.org/2000/svg">
      <g clip-path="url(#1gy7h05xha)">
        <path d="M20 3.75A11.658 11.658 0 0 0 8.333 15.418C8.333 24.167 20 37.084 20 37.084s11.667-12.917 11.667-21.667c0-6.45-5.217-11.666-11.667-11.666zm0 15.834a4.168 4.168 0 0 1-4.167-4.167c0-2.3 1.867-4.166 4.167-4.166s4.167 1.866 4.167 4.166c0 2.3-1.867 4.167-4.167 4.167z" fill="${color}"/>
      </g>
      <defs>
        <clipPath id="1gy7h05xha">
          <path transform="translate(0 .417)" d="M0 0h40v40H0z"/>
        </clipPath>
      </defs>
    </svg>
    `;
  }

  openInfoWindow(index: number): void {
    if (this.selectedIndex !== undefined) {
      this.infoWindows.get(this.selectedIndex)?.close();
    }
    this.infoWindows.get(index)?.open();
    this.selectedIndex = index;
  }

  onInfoWindowClose(index: number): void {
    if (this.selectedIndex !== index) return;
    this.selectedIndex = undefined;
    this.tableCell.nativeElement.scrollTop = 0;
  }

  scrollTableRow(index: number): void {
    const rowHeight = 34;
    this.tableCell.nativeElement.scrollTop = (this.dataSource.length - index) * rowHeight - rowHeight;
  }
}