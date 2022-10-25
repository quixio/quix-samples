import {Component, OnInit} from '@angular/core';
import {QuixService} from "../../services/quix.service";
import {HttpClient} from "@angular/common/http";
import {Guid} from 'guid-typescript';
import {ActivatedRoute} from "@angular/router";

@Component({
    selector: 'app-lobby',
    templateUrl: './lobby.component.html',
    styleUrls: ['./lobby.component.scss']
})
export class LobbyComponent implements OnInit {

    public qrInfo: string = "";
    public qrId: Guid;
    private interval: NodeJS.Timeout;
    public timeLeft: number = 0;
    private expiry: number = 0;
    hasUsername = false;
    device: string = "";
    processing: boolean = false;
    public additionalProperties = {};
    newKey: string = "";
    newValue: string = "";
    private tokenTimerInterval: NodeJS.Timeout;
    private tokenExpiry: Date;
    private tokenId: string;
    public firstPageError: string = "";
    public showWorkingOnItMessage: boolean = false;
    username: string = "";

    public AddProp() {
        this.additionalProperties[this.newKey] = this.newValue;
        this.newKey = "";
        this.newValue = "";
    }

    public DelProp(key) {
        delete this.additionalProperties[key];
    }

    constructor(private quixService: QuixService,
                private httpClient: HttpClient,
                private route: ActivatedRoute) {
    }

    ngOnInit(): void {
        this.quixService.startHubConnection();

        this.route.queryParams
            .subscribe(params => {
                Object.keys(params).forEach(key => {
                    this.additionalProperties[key] = params[key];
                });
            });

        this.quixService.PersonalAccessTokenCreationError.subscribe(error => {
           console.log(error)
            if(error?.error?.message?.includes("exists")){
                this.generateTokenId();
            }
        });
        this.quixService.PersonalAccessTokenReceived.subscribe(data => {
            if (data.name === this.tokenId) {
                console.log(data);
                this.stopTokenTimer();
                this.showWorkingOnItMessage = false;
                this.PushSettings(data.token);
            }
        });
    }

    startTimer() {
        this.interval = setInterval(() => {
            this.timeLeft = (this.expiry - Date.now()) / 1000;
            if (this.timeLeft <= 0) {
                this.stopTimer();
            }
        }, 400)
    }

    stopTimer() {
        clearInterval(this.interval);
        this.qrInfo = "";
    }

    tokenTimeLeft = 3000;
    startTokenTimer() {
        this.showWorkingOnItMessage = false;
        this.tokenTimeLeft = 3000;
        this.tokenTimerInterval = setInterval(() => {
            this.tokenTimeLeft -= 500;
            console.log("Time token until retry = " + this.tokenTimeLeft);
            if (this.tokenTimeLeft <= 0) {
                this.tokenTimeLeft = 3000;
                this.quixService.createPersonalAccessToken(this.tokenId, this.tokenExpiry);
                this.showWorkingOnItMessage = true;
            }
        }, 500)
    }

    stopTokenTimer() {
        clearInterval(this.tokenTimerInterval);
    }

    ok_click() {
        this.processing = true;
        this.generateToken();
    }

    generateTokenId(){
        let oneDay = (1000 * 60 * 60 * 24);
        this.tokenExpiry = new Date(Date.now() + oneDay * 30); //30 day token
        this.tokenId = this.username + "_" + this.device + "_" + new Date().toISOString();
    }

    generateToken() {
        this.generateTokenId();
        this.quixService.createPersonalAccessToken(this.tokenId, this.tokenExpiry);
        this.startTokenTimer();
    }

    PushSettings(token) {

        let coreProperties = {
            'bearerToken': token,
            'workspaceId': this.quixService.workspaceId,
            'subdomain': this.quixService.subdomain
        }

        this.qrId = Guid.create();
        this.expiry = Date.now() + (60 * 1000);

        let combinedProperties = Object.assign({}, coreProperties, this.additionalProperties);

        this.quixService.PushSettings(this.qrId.toString(), combinedProperties, this.expiry,
            (qrString) => {
                this.startTimer();
                this.qrInfo = JSON.stringify(qrString);
                this.processing = false;
            });

    }

    saveUserName() {
        this.hasUsername = this.username !== '' && this.device !== '';
        this.firstPageError = "Please enter a Username and Device to assign to the token.";
    }
}
