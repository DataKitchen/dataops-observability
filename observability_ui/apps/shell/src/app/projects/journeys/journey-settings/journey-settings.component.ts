import { Component, OnInit } from '@angular/core';
import { merge, tap } from 'rxjs';
import { CoreComponent, omit, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { JourneysStore } from '../journeys.store';
import { BaseComponent, Journey, JourneyInstanceRule } from '@observability-ui/core';
import { ConfirmDialogComponent } from '@observability-ui/ui';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { JourneysService } from '../../../services/journeys/journeys.service';
import { takeUntil } from 'rxjs/operators';

@Component({
  selector: 'shell-journey-settings',
  templateUrl: './journey-settings.component.html',
  styleUrls: [ './journey-settings.component.scss' ]
})
export class JourneySettingsComponent extends CoreComponent implements OnInit {
  private projectId: string;

  journey$ = this.store.selected$.pipe(
    tap((journey) => {
      this.projectId = journey.project;
      this.form.patchValue({
        id: journey?.id,
        name: journey?.name,
        description: journey?.description,
        component_include_patterns: journey?.component_include_patterns ?? null,
        component_exclude_patterns: journey?.component_exclude_patterns ?? null,
        instance_rules: journey?.instance_rules.filter(rule => rule.action !== 'END_PAYLOAD') ?? [],
        payload_instance_conditions: journey?.instance_rules.filter(rule => rule.action === 'END_PAYLOAD') ?? [],
      });

      if (journey.id) {
        this.store.dispatch('findComponents', journey.id);
      }
    }),
  );
  components$ = this.store.components$;

  saving$ = this.store.getLoadingFor('updateOne');

  previewResults: Pick<BaseComponent, 'key' | 'name'>[] | null = null;
  previewing = false;

  form = new TypedFormGroup<{
    id: string;
    name: string;
    description: string;
    component_include_patterns: string | null;
    component_exclude_patterns: string | null;
    instance_rules: JourneyInstanceRule[]
    payload_instance_conditions: JourneyInstanceRule[],
  }>({
    id: new TypedFormControl<string>(),
    name: new TypedFormControl<string>(''),
    description: new TypedFormControl<string>(''),
    component_include_patterns: new TypedFormControl<string | null>(null),
    component_exclude_patterns: new TypedFormControl<string | null>(null),
    instance_rules: new TypedFormControl([]),
    payload_instance_conditions: new TypedFormControl([]),
  });

  constructor(
    private store: JourneysStore,
    private journeysService: JourneysService,
    private dialog: MatDialog,
    private router: Router,
    private route: ActivatedRoute,
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();

    merge(
      this.form.controls.component_include_patterns.valueChanges,
      this.form.controls.component_exclude_patterns.valueChanges,
    ).pipe(takeUntil(this.destroyed$)).subscribe(() => this.previewResults = null);
  }

  saveInfo(original: Journey): void {
    this.store.dispatch('updateOne', {
      ...omit(this.form.value, [ 'payload_instance_conditions' ]),
      instance_rules: (original.instance_rules ?? []),
    });
  }

  cancelInfoChanges(original: Journey): void {
    this.form.patchValue({
      name: original.name,
      description: original.description,
      component_include_patterns: original.component_include_patterns ?? null,
      component_exclude_patterns: original.component_exclude_patterns ?? null,
    });
    this.previewResults = null;
  }

  previewComponents(): void {
    this.previewing = true;
    this.journeysService.previewComponentPatterns(
      this.projectId,
      this.form.value.component_include_patterns,
      this.form.value.component_exclude_patterns,
    ).pipe(takeUntil(this.destroyed$)).subscribe({
      next: (components) => {
        this.previewResults = components;
        this.previewing = false;
      },
      error: () => {
        this.previewing = false;
      },
    });
  }

  saveConditions() {
    this.store.dispatch('updateOne', {
      ...omit(this.form.value, [ 'payload_instance_conditions' ]),
      instance_rules: [ ...this.form.value.instance_rules, ...this.form.value.payload_instance_conditions ]
    });
  }

  cancelConditionsChanges(original: Journey): void {
    this.form.patchValue({ instance_rules: original.instance_rules ?? [] });
  }

  openConfirmDialog(journey: Journey) {
    const dialogRef = this.dialog.open(ConfirmDialogComponent, {
      data: {
        title: 'Delete Journey',
        message: `Are you sure you want to delete journey "${journey.name}"?`,
        confirmLabel: 'Delete',
        id: journey.id,
        confirmButtonColor: 'warn'
      }
    });

    dialogRef.afterClosed().subscribe((data) => {
      if (data) {
        this.store.dispatch('deleteOne', data.id);
        void this.router.navigate([ '../../' ], {
          relativeTo: this.route,
        });
      }
    });
  }

}
