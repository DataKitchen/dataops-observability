import { Component, Inject, Optional } from '@angular/core';
import { AppVersionService } from './app-version/app-version.service';
import { SessionService, EntitiesResolver, ProjectStore } from '@observability-ui/core';
import { filter, tap } from 'rxjs';
import { ComponentType } from '@angular/cdk/portal';
import { REPLACEMENT_TOKENS } from '../app/config';

@Component({
  selector: 'shell-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent {

  isAuth$ = this.sessionService.isLoggedIn$;
  currentProject$ = this.projectStore.current$;
  constructor(
    private sessionService: SessionService,
    private appVersion: AppVersionService,
    private entities: EntitiesResolver,
    private projectStore: ProjectStore,
    @Optional() @Inject(REPLACEMENT_TOKENS.HeaderComponent) public headerComponent?: ComponentType<any>,
  ) {
    this.appVersion.currentVersion$.subscribe((version) => {
      console.log({version});
    });

    this.entities.organization$.pipe(
      tap(({id}) => {
        this.projectStore.dispatch('findAll', {parentId: id});
      })
    ).subscribe();

    this.sessionService.user$.pipe(
      filter(Boolean),
      tap((user) => {
        this.entities.dispatch('getCompany', user.primary_company);
        this.entities.dispatch('getOrganizations', user.primary_company);
      }),
    ).subscribe();
  }

}
