import { Injectable } from '@angular/core';
import { UrlTree } from '@angular/router';
import { map } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { SessionService } from '../../services/auth/session.service';

@Injectable({ providedIn: 'root' })
export class NoAuthGuard  {
    constructor(private sessionService: SessionService) {}

    canActivate(): Observable<boolean | UrlTree> {
        return this.sessionService.isLoggedIn$.pipe(
            map((isLoggedIn) => !isLoggedIn),
        );
    }
}
