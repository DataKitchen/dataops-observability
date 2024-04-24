import { Injectable } from '@angular/core';
import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { EMPTY, Observable, tap } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatLegacySnackBar as MatSnackBar } from '@angular/material/legacy-snack-bar';
import { SessionService } from '../services';

@Injectable()
export class BaseHttpInterceptor implements HttpInterceptor {

  private static readonly excludedDomains = [ '/v1/auth/basic' ];

  constructor(
    private snackbar: MatSnackBar,
    private sessionService: SessionService,
  ) {
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (this.isExcluded(request.url)) {
      return next.handle(request);
    }

    const token = this.sessionService.getToken();
    if (token) {
      request = request.clone({
        setHeaders: {Authorization: `Bearer ${token}`}
      });
    }

    return next.handle(request).pipe(
      catchError(async (error) => this.handleError(error))
    ) as Observable<HttpEvent<any>>;
  }

  private async handleError(response: HttpErrorResponse) {
    const {status} = response;
    if (status === 401 || status === 403) {
      this.sessionService.removeToken();
      this.snackbar.open('Your session has expired. Please login again', 'Login').onAction().pipe(
        tap(() => {
          window.location.href = '/authentication/login';
        }),
      ).subscribe();
      return EMPTY;
    }
    throw response;
  }

  private isExcluded(url: string): boolean {
    return BaseHttpInterceptor.excludedDomains.some(substring => url.includes(substring));
  }
}
