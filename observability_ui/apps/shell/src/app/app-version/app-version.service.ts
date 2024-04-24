import { Injectable } from '@angular/core';
import { SwUpdate } from '@angular/service-worker';
import { BehaviorSubject, combineLatest, filter, fromEvent, interval, map, ReplaySubject, startWith, take, tap } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { MatBottomSheet } from '@angular/material/bottom-sheet';
import { AppVersionComponent } from './app-version.component';

export interface AppVersion {
  hash: string;
  [app: string]: string;
}

@Injectable({
  providedIn: 'root'
})
export class AppVersionService {

  currentVersion$: ReplaySubject<AppVersion> = new ReplaySubject<AppVersion>();
  nextVersion$: BehaviorSubject<AppVersion | undefined> = new BehaviorSubject<AppVersion | undefined>(undefined);

  onFocus$ = fromEvent(document, 'visibilitychange').pipe(
    startWith(document),
    map(() => document.visibilityState === 'visible')
  );
  constructor(
    bottomSheet: MatBottomSheet,
    private updates: SwUpdate,
    private http: HttpClient,
  ) {
    if (updates.isEnabled) {

      this.http.get<{appData: AppVersion}>('/ngsw.json').pipe(
        take(1),
        map(({appData}) => appData),
        tap((version) => {
          console.log('app version', version);
        })
      ).subscribe(this.currentVersion$);

      const count = 60;
      console.log('will check for updates every', count, 'secs');
      const timelapse$ = interval( count * 1000);

      combineLatest([
        timelapse$,
        this.onFocus$,
      ]).pipe(
        // do not check for updates when page does not have focus
        filter(([ , isVisible ]) => isVisible),
      ).subscribe(() => {
        console.log('checking for updates');
        void updates.checkForUpdate();
      });

      updates.versionUpdates.subscribe((evt) => {
        console.log('version event:', evt);
        switch (evt.type) {
          case 'VERSION_DETECTED':
            console.log('Downloading new app version:', evt);
            break;
          case 'VERSION_READY':
            console.log('Current app version:', evt);
            console.log('New app version ready for use:', evt);
            this.nextVersion$.next(<AppVersion>evt.latestVersion.appData);
            bottomSheet.open(AppVersionComponent);
            break;
          case 'VERSION_INSTALLATION_FAILED':
            console.log(`Failed to install app version '${evt.version.hash}': ${evt.error}`);
            break;
        }

      });
    }
  }
}
