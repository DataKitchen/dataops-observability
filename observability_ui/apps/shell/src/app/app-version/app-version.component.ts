import { Component } from '@angular/core';
import { AppVersionService } from './app-version.service';

@Component({
  selector: 'shell-app-version',
  templateUrl: './app-version.component.html',
  styleUrls: [ './app-version.component.css' ]
})
export class AppVersionComponent {

  newVersion$ = this.appVersion.nextVersion$;

  constructor(
    private appVersion: AppVersionService,
  ) {}

  reloadPage() {
    window.location.reload();
  }
}
