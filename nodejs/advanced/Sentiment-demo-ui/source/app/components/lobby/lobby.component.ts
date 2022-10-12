import {Component, OnInit, Output} from '@angular/core';
import {QuixService} from "../../services/quix.service";
import {ActivatedRoute, Router} from "@angular/router";

@Component({
  selector: 'app-lobby',
  templateUrl: './lobby.component.html',
  styleUrls: ['./lobby.component.scss']
})
export class LobbyComponent implements OnInit {

  public room: string;
  public message: string;
  public name: string;
  public phone: string;
  public email: string;

  constructor(private quixService: QuixService,
              private route: ActivatedRoute,
              private router: Router) { }

  ngOnInit(): void {
    this.room = this.route.snapshot.queryParams["room"];
  }

  connect(){
    this.router.navigate(["webchat", this.room, this.name], {queryParams:{
        "email": this.email,
        "phone": this.phone
      }})
  }

  canConnect() {
    return this.room?.length > 0 && this.name?.length > 0;
  }

}