import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';

interface Connection { room: string, name: string, phone?: string, email?: string };

@Component({
  selector: 'app-lobby',
  templateUrl: './lobby.component.html',
  styleUrls: ['./lobby.component.scss']
})
export class LobbyComponent implements OnInit {
  storedConnection: Connection;

  form = new FormGroup({
    room: new FormControl('', [Validators.required]),
    name: new FormControl('', [Validators.required]),
    phone: new FormControl(undefined),
    email: new FormControl(undefined)
  });

  constructor(private route: ActivatedRoute, private router: Router) { }

  ngOnInit(): void {
    const room = this.route.snapshot.queryParamMap.get('room');
    if (room) this.form.controls.room.setValue(room);

    const localStorageValue = localStorage.getItem('connection');
    if (localStorageValue) this.storedConnection = JSON.parse(localStorageValue);
  }

  submit() {
    if (this.form.invalid) return;
    const connection = this.form.value as Connection;
    localStorage.setItem('connection', JSON.stringify(connection));
    this.connect(connection);
  }

  connect(connection: Connection) {
    this.router.navigate(['webchat', connection.room.toLowerCase(), connection.name], {
      queryParams: {
        'email': connection.email,
        'phone': connection.phone
      }
    })
  }
}