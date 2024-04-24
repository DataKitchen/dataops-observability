import { Injectable } from '@angular/core';
import { AppConfiguration } from './app-configuration';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  readonly ready$: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);

  private config!: AppConfiguration;

  setConfig(c: AppConfiguration) {
    this.config = c;
    this.ready$.next(true);
  }

  get<K extends keyof AppConfiguration>(k: K): AppConfiguration[K] {
    if (k === 'apiBaseUrl') {
      return this.getApiUrl() as AppConfiguration[K];
    }

    return this.config[k];
  }

  private getApiUrl(): AppConfiguration['apiBaseUrl'] {
    return this.config.apiBaseUrl;
  }
}
