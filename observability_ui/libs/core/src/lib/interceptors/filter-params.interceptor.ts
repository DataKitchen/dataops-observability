import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class FilterParamsInterceptor implements HttpInterceptor {
  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (request.params) {
      request = request.clone({ params: this.filterInvalidParams(request.params) });
    }
    return next.handle(request);
  }

  private filterInvalidParams(params: HttpParams): HttpParams {
    let filteredParams = new HttpParams();
    for (const key of params.keys()) {
      const values = params.getAll(key) ?? [];
      for (const v of values) {
        if (this.isValid(v)) {
          filteredParams = filteredParams.append(key, v);
        }
      }
    }
    return filteredParams;
  }

  private isValid(value: string | number | boolean): boolean {
    return value !== 'null'
      && value !== 'undefined'
      && value !== null
      && value !== undefined
      && value !== ''
      && !Number.isNaN(value);
  }
}
