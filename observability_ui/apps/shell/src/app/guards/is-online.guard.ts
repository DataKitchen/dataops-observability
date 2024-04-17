import { Injectable } from '@angular/core';
import { Router, UrlTree } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class IsOnlineGuard  {
  constructor(private router: Router) {}

  canActivate(): boolean | UrlTree {
    return navigator.onLine || this.router.parseUrl('/offline');
  }

}
