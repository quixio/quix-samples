import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormGroupDirective, Validators } from '@angular/forms';
import { Guid } from 'guid-typescript';
import { QuixService } from "../../services/quix.service";

@Component({
  selector: 'app-lobby',
  templateUrl: './lobby.component.html',
  styleUrls: ['./lobby.component.scss']
})
export class LobbyComponent implements OnInit {
  qrInfo: string = "";
  qrId: Guid;
  timeLeft: number = 0;
  processing: boolean = false;
  tokenExpiration: Date;
  private _expiry: number = 0;
  private _interval: NodeJS.Timer;
  private _tokenExpiry: Date;
  private _tokenId: string;

  form = new FormGroup({
    name: new FormControl('', [Validators.required]),
    deviceId: new FormControl('', [Validators.required]),
  });

  tokenData: any;

  constructor(private quixService: QuixService) {
  }

  ngOnInit(): void {
    this.quixService.PersonalAccessTokenCreationError.subscribe(error => {
      console.log(error)
      if (error?.error?.message?.includes("exists")) {
        this.generateToken();
      }
    });
    this.quixService.PersonalAccessTokenReceived.subscribe(data => {
      if (data.name === this._tokenId) {
        console.log(data);
        this.pushSettings(data.value);
        this.tokenExpiration = data.expiresAt;
      }
    });
  }

  startTimer() {
    this._interval = setInterval(() => {
      this.timeLeft = (this._expiry - Date.now()) / 1000;
      if (this.timeLeft <= 0) {
        clearInterval(this._interval);
        this.qrInfo = "";
        this.tokenData = undefined;
      }
    }, 400);
  }


  generateToken() {
    let oneDay = (1000 * 60 * 60 * 24);
    this._tokenExpiry = new Date(Date.now() + oneDay * 365); //30 day token
    this._tokenId = this.tokenData.name + "_" + this.tokenData.deviceId + "_" + new Date().toISOString();
    this.quixService.createPersonalAccessToken(this._tokenId, this._tokenExpiry);
  }

  pushSettings(token: string) {
    let coreProperties = {
      'bearerToken': token,
      'workspaceId': this.quixService.workspaceId,
      'subdomain': this.quixService.subdomain,
      'rider': this.tokenData.name,
      'device': this.tokenData.deviceId
    }

    this.qrId = Guid.create();
    this._expiry = Date.now() + (60 * 1000);

    console.log("Pushing token to API. Token ID = " + this.qrId);
    this.quixService.pushSettings(this.qrId.toString(), coreProperties, this._expiry,
      (qrString: string) => {
        this.startTimer();
        this.qrInfo = JSON.stringify(qrString);
        this.processing = false;
      });
  }

  submit(formDirective: FormGroupDirective) {
    if (!this.form.valid) return;
    this.tokenData = this.form.value;
    this.form.reset();
    formDirective.resetForm();
    this.processing = true;
    this.generateToken();
  }
}