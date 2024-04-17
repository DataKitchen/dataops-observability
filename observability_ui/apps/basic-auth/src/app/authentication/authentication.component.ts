import { Component } from '@angular/core';

@Component({
  selector: 'auth-entry',
  template: `<router-outlet></router-outlet>`,
  styles: [`
    :host {
      width: 100%;
      height: 100%;
    }
  `],
})
export class AuthenticationComponent {}
