import { Inject, Injectable } from '@angular/core';
import { Observable, Subject } from 'rxjs';
import { DOCUMENT } from '@angular/common';

@Injectable({
  providedIn: 'root',
})
export class ClickListenerService {

  private _onClick: Subject<MouseEvent> = new Subject<MouseEvent>();

  constructor(@Inject(DOCUMENT) private document: Document) {
    this.document.addEventListener('click', this.clicked.bind(this));
  }

  get onClick(): Observable<MouseEvent> {
    return this._onClick.asObservable();
  }

  private clicked($event: MouseEvent) {
    this._onClick.next($event);
  }

}
