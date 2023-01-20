import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { Alert } from 'src/app/models/alert';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-alerts-dialog',
  templateUrl: './alerts-dialog.component.html',
  styleUrls: ['./alerts-dialog.component.scss']
})
export class AlertsDialogComponent {
  alerts: Alert[];
  unreadAlertsCount: number;

  constructor(
    @Inject(MAT_DIALOG_DATA) private data: any,
    private dilogRef: MatDialogRef<AlertsDialogComponent>,
    private userService: UserService
  ) { 
    this.alerts = data.alerts;
    this.unreadAlertsCount = data.unreadAlertsCount;
  }

  setStreamId(streamId: string) {
    this.userService.setStreamId(streamId);
    this.close()
  }

  close(): void {
    this.dilogRef.close();
  }
}
