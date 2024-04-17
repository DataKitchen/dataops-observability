import {Component, ElementRef, OnDestroy, ViewChild} from '@angular/core';
import {MatLegacyTabNav as MatTabNav} from '@angular/material/legacy-tabs';
import {ActivatedRoute, Router} from '@angular/router';
import {OnHostResized, RunAlertType, RunProcessedStatus} from '@observability-ui/core';
import {combineLatest, filter, fromEvent, map, startWith, tap, timer, withLatestFrom} from 'rxjs';
import {RunsStore} from '../../../stores/runs/runs.store';
import {takeUntilDestroyed} from "@angular/core/rxjs-interop";

@Component({
  selector: 'shell-run-details',
  templateUrl: './run-details.component.html',
  styleUrls: ['./run-details.component.scss']
})
export class RunDetailsComponent implements OnDestroy {
  @ViewChild('tabs') tabs: MatTabNav;

  run$ = this.runStore.selected$.pipe(
    tap((run) => {
      if (run.status === RunProcessedStatus.Pending || run.status === RunProcessedStatus.Missing) {

        // navigate back if run is pending or missing...
        // @luis wouldn't be better to void the link in the run list page
        // so that the user cannot reach this page?
        void this.router.navigate(['..']);
      }
    })
  );

  protected readonly RunAlertType = RunAlertType;

  private onFocus$ = fromEvent(document, 'visibilitychange').pipe(
    startWith(document),
    filter(() => document.visibilityState === 'visible')
  );

  private refresh$ = combineLatest([
    timer(0, 60 * 1000),
    this.onFocus$
  ]).pipe(
    filter(() => document.visibilityState === 'visible'),
    withLatestFrom(this.run$),
    filter(([, run]) => {
      // do not refresh if the run is finished
      return run?.status !== RunProcessedStatus.Running;
    }),
    startWith(null),
  );

  constructor(
    private element: ElementRef,
    private router: Router,
    private route: ActivatedRoute,
    private runStore: RunsStore,
  ) {
    combineLatest([
      this.refresh$,
      this.route.params.pipe(
        map(({runId}) => runId as string),
        startWith(this.route.snapshot.params['runId'] as string),
      ),
    ]).pipe(
      takeUntilDestroyed(),
    ).subscribe(([, id]) => {
      this.runStore.dispatch('getOne', id);
    });

  }

  @OnHostResized()
  alignInkBar(): void {
    this.tabs?._alignInkBarToSelectedTab();
  }

  ngOnDestroy(): void {
    this.runStore.dispatch('reset');
  }
}
