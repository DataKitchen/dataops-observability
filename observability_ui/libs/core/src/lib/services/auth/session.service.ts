import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, of, shareReplay, switchMap, map } from 'rxjs';
import { cookieKeys, cookiePath, localStorageKeys } from './auth.model';
import { CookieService } from 'ngx-cookie-service';
import { JwtHelperService } from '@auth0/angular-jwt';
import { ConfigService } from '../../config/config.service';
import { User } from '../user/user.model';
import { Router } from '@angular/router';


@Injectable({ providedIn: 'root' })
export class SessionService {
  isLoggedIn$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  user$: Observable<User | null> = this.isLoggedIn$.pipe(
    switchMap((isAuth) => {
      if (isAuth) {
        return this.getUser();
      }

      return of(null);
    }),
    shareReplay(),
  );

  constructor(
    private http: HttpClient,
    private router: Router,
    private cookieService: CookieService,
    private jwtHelperService: JwtHelperService,
    private configService: ConfigService,
  ) {
    if (this.isLoggedIn()) {
      this.isLoggedIn$.next(true);
    }
  }

  setLoginRedirect(url: string) {
    localStorage.setItem(localStorageKeys.loginRedirect, url);
  }

  getLoginRedirect(): string | undefined {
    const url: string = localStorage.getItem(localStorageKeys.loginRedirect) as string;
    return url;
  }

  getToken() {
    return this.cookieService.get(cookieKeys.token);
  }

  setToken(token: string): void {
    this.cookieService.set(cookieKeys.token, token, { path: cookiePath });
  }

  removeToken(): void {
    this.cookieService.delete(cookieKeys.token, cookiePath);
  }

  endSession(): void {
    this.isLoggedIn$.next(false);
    // Tick is needed to avoid the navigation from being canceled by competing routing by BindQueryParams
    setTimeout(() => this.router.navigate(['/authentication/logout']));
  }

  private getUser(): Observable<User> {
    const userId = this.getUserId();
    const params = { expand_created_by: true, expand_primary_company: true };
    return this.http.get<User>(`${this.baseUrl}/observability/v1/users/${userId}`, { params }).pipe(
      map(user => user),
    );
  }

  private isLoggedIn() {
    return !!this.getToken() && !this.jwtHelperService.isTokenExpired(this.getToken());
  }

  /* istanbul ignore next */
  private getUserId(): string {
    const token = this.getToken();
    const claims = this.jwtHelperService.decodeToken(token);
    return claims.user_id;
  }

  private get baseUrl(): string {
    return this.configService.get('apiBaseUrl') as string;
  }
}
