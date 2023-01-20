import { Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private _streamIdChange$ = new Subject<string>();

  get streamId$() {
    return this._streamIdChange$.asObservable();
  }

  constructor() { }

  setStreamId(streamId: string): void {
    this._streamIdChange$.next(streamId);
  }
}
