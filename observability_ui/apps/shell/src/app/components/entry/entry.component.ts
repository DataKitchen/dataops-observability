import { Component, OnDestroy, OnInit } from '@angular/core';
import { takeUntil, tap } from 'rxjs';
import { Router } from '@angular/router';
import { ProjectStore } from '@observability-ui/core';
import { CoreComponent } from '@datakitchen/ngx-toolkit';

@Component({
  selector: 'shell-entry',
  template: `
    <div fxFlexFill fxLayoutAlign="center center">
      <mat-progress-spinner mode="indeterminate" color="primary"></mat-progress-spinner>
    </div>
  `,
  styles: [`
    :host {
      height: 100%;
      width: 100%;
    }
  `]
})
export class EntryComponent extends CoreComponent implements OnInit, OnDestroy {

  constructor(
    private router: Router,
    private projectStore: ProjectStore,
  ) {
    super();
  }

  override ngOnInit(): void {
    super.ngOnInit();

    this.projectStore.current$.pipe(
      tap((project) => {
        void this.router.navigate(['/', 'projects', project.id]);
      }),
      takeUntil(this.destroyed$),
    ).subscribe();

  }

}
