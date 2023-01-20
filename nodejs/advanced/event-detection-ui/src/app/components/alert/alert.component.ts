import { Component, Inject, Input, OnInit } from '@angular/core';
import { MatSnackBar, MAT_SNACK_BAR_DATA } from '@angular/material/snack-bar';
import { Alert } from 'src/app/models/alert';
import { UserService } from 'src/app/services/user.service';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.component.html',
  styleUrls: ['./alert.component.scss']
})
export class AlertComponent {
  alert: Alert;

  constructor(@Inject(MAT_SNACK_BAR_DATA) private data: any, private userService: UserService) {
    this.alert = data.alert;
  }

  setStreamId(streamId: string) {
    this.userService.setStreamId(streamId);
    this.dismiss()
  }

  dismiss() {
    this.data.preClose();
  }
}
