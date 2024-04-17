import { Component } from '@angular/core';
import { ProjectStore } from '@observability-ui/core';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { filter, tap } from 'rxjs';

@Component({
  selector: 'shell-project-display',
  template: `
    <div class="project-container"
      *ngIf="currentProject()">
      <div class="project-label">Project</div>
      <div class="project-value">{{currentProject().name}}</div>
    </div>
  `,
  styleUrls: [ 'project-display.component.scss' ]
})

export class ProjectDisplayComponent {
  currentProject = toSignal(this.projectStore.current$);

  constructor(
    private router: Router,
    private projectStore: ProjectStore,
    private route: ActivatedRoute,
  ) {
    /**
     * Attention! This is a crucial point because it makes sure that the
     * `projectId` on the url correctly sets the current project in
     * projectStore. Without this pretty much everything stops to load in
     * `ProjectModule`
     */
    this.route.params.pipe(
      tap(({projectId}) => {
        this.projectStore.dispatch('getOne', projectId);
      }),
      takeUntilDestroyed(),
    ).subscribe();

    this.projectStore.loading$.pipe(
      filter(({code}) => code === 'getOne'),
      filter(({error}) => !!error),
      tap(({payload}) => {
        this.projectStore.dispatch('reset');
        void this.router.navigate(['/'], {replaceUrl: true});
        throw new Error(`The project "${payload}" does not exist. You've been redirected to the default project.`);
      }),
      takeUntilDestroyed()
    ).subscribe();
  }
}
