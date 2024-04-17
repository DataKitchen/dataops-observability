import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router, UrlTree } from '@angular/router';
import { ConfigService, SessionService } from '@observability-ui/core';
import { Observable, map, tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class BasicAuthService {
  constructor(
    private http: HttpClient,
    private router: Router,
    private configService: ConfigService,
    private sessionService: SessionService,
  ) {}

  login(credentials: { username: string; password: string; }): Observable<UrlTree> {
    this.sessionService.removeToken();
    return this.http.get<{ token: string }>(`${this.configService.get('apiBaseUrl')}/observability/v1/auth/basic`, {
      headers: {
        Authorization: `Basic ${this.encodeCredentials(credentials)}`,
      }
    }).pipe(
      map((response) => {
        this.sessionService.setToken(response.token);
        this.sessionService.isLoggedIn$.next(true);

        return this.router.parseUrl(this.sessionService.getLoginRedirect() ?? '/');
      }),
    );
  }

  logout(): Observable<any> {
    return this.http.get(`${this.configService.get('apiBaseUrl')}/observability/v1/auth/logout`).pipe(
      tap(() => this.sessionService.removeToken()),
    );
  }

  private encodeCredentials(credentials: { username: string; password: string; }): string {
    return btoa(`${credentials.username}:${credentials.password}`);
  }
}
