import { Component, HostListener, OnInit } from '@angular/core';
import { QuixService } from "./services/quix.service"
import {WebcamImage, WebcamUtil} from 'ngx-webcam';
import { Observable, startWith, Subject, switchMap, timer } from 'rxjs';
import { MatSelectChange } from '@angular/material/select';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {

  devices: MediaDeviceInfo[] = [];
  refreshRates: number[] = [0.25, 0.5, 1, 2, 3, 5, 10];
  inputDevice: MediaDeviceInfo;
  refreshRate: number = 2;
  webcamImage: WebcamImage;
  lastImageTaken: number;
  width = 1080;
  lat: number = 0;
  long: number = 0;
  private intervalId: NodeJS.Timer;


  private reset$ = new Subject();
  timer$: Observable<any>;

  // webcam snapshot trigger
  private trigger: Subject<void> = new Subject<void>();

  constructor(private envVarService: QuixService) {}

  @HostListener('window:resize', ['$event'])
  onResize(event: any) {
    const pagePadding = 80;

    // If it's less than 300, then don't go any smaller
    if (event.target.innerWidth - pagePadding < 300) return;

    // If it's greater than 768 (breakpoint) then set width
    // to half the size of the screen. Else we set it to the
    // fall width of the screen.
    if (window.innerWidth > 768) {
      this.width = (window.innerWidth / 2) - (pagePadding / 2);
    } else {
      this.width = event.target.innerWidth - pagePadding;
    }

  }

  ngOnInit(): void {
    // Dispatch a fake resize to trigger the resize of the webcam component
    window.dispatchEvent(new Event('resize'));

    // Get all available video outputs and put them in dropdown to
    // allow the user to select webcam source
    this.getVideoInputs()
	
	// retry getting video inputs every 2 seconds.
	// needed if the user has to give permission else the 
	// code to populate the drop down will not be called again
    this.intervalId = setInterval(() => this.getVideoInputs(), 2000);

    this.setupTimer();
  }

  private getVideoInputs(){
    WebcamUtil.getAvailableVideoInputs()
        .then((mediaDevices: MediaDeviceInfo[]) => {
          this.devices = mediaDevices;
          // If there is at least one device with an ID then set that as the default
          if (mediaDevices.length > 0 && mediaDevices[0].deviceId !== "") {
            this.inputDevice = mediaDevices[0];
            clearInterval(this.intervalId)
          }
        });

  }

  public deviceChanged(event: MatSelectChange): void {
    const { value } = event;
    this.inputDevice = value;
  }

  /**
   * Triggered when the user selects a different refresh rate
   */
  public refreshRateChanged():void {
    this.reset$.next(void 0);
  }

  /**
   * Setup the timer which will trigger a snapshot of the video input
   * every x seconds. Configured by user in dropdown.
   */
  private setupTimer(): void {
    this.timer$ = this.reset$.pipe(
      startWith(0),
      switchMap(() => timer(0, this.refreshRate * 1000))
    );

    this.timer$.subscribe(() => {
      this.triggerSnapshot();
      this.envVarService.sendDataToQuix(this.webcamImage);
    });
  }

  public triggerSnapshot(): void {
    this.trigger.next();
  }



  /**
   * Output from the webcam component when it takes a snapshot
   * @param webcamImage the image captured from web cam
   */
  public handleImage(webcamImage: WebcamImage): void {
    this.lastImageTaken = Date.now();
    this.webcamImage = webcamImage;
  }

  /**
   * Observable of the trigger used for snapshots
   */
  public get triggerObservable(): Observable<void> {
    return this.trigger.asObservable();
  }
}
