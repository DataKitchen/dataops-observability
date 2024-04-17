import { Component, OnDestroy, OnInit } from '@angular/core';
import { combineLatest, map, Observable, startWith, takeUntil, tap } from 'rxjs';
import { BaseComponent } from '@observability-ui/core';
import { ActivatedRoute } from '@angular/router';
import { Rule } from '../../../components/rules-actions/rule.model';
import { RuleStore } from '../../../components/rules-actions/rule.store';
import { RuleDisplayComponent } from '../../../components/rules-actions/rule-display/rule-display.component';
import { JourneysStore } from '../journeys.store';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { CoreComponent } from '@datakitchen/ngx-toolkit';

@Component({
  selector: 'shell-journey-rules-component',
  templateUrl: 'journey-rules.component.html',
  styleUrls: [ 'journey-rules.component.scss' ],
})
export class JourneyRulesComponent extends CoreComponent implements OnInit, OnDestroy {

  journeyId$: Observable<string> = this.route.parent!.params.pipe(
    map(({id}) => id),
    tap((id) => {
      // store it for later use
      this.journeyId = id;
    })
  );

  rules$: Observable<Rule[]> = this.store.list$;

  loading$ = this.store.getLoadingFor('findAll').pipe(
    startWith(true),
  );

  components: BaseComponent[];
  components$ = this.journeyStore.components$;

  private journeyId: string;

  constructor(
    private store: RuleStore,
    private journeyStore: JourneysStore,
    private route: ActivatedRoute,
    private dialog: MatDialog,
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();

    combineLatest([
      this.journeyId$,
    ]).pipe(
      tap(([ id ]) => {
        this.store.dispatch('findAll', {parentId: id});
        this.journeyStore.dispatch('findComponents', id);
      }),
      takeUntil(this.destroyed$),
    ).subscribe();

    this.components$.pipe(
      tap((components) => {
        this.components = components;
      }),
      takeUntil(this.destroyed$),
    ).subscribe();
  }

  openRuleDialog() {
    this.dialog.open(RuleDisplayComponent, {
      minWidth: '720px',
      maxWidth: '820px',
      maxHeight: '90vh',
      panelClass: 'overflow-auto',
      autoFocus: 'dialog',
      data: {
        parentId: this.journeyId,
        editing: true,
        components: this.components,
      }
    });
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    this.store.dispatch('reset');
  }
}
