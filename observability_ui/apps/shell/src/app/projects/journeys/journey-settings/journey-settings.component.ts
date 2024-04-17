import { Component } from '@angular/core';
import { tap } from 'rxjs';
import { CoreComponent, omit, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { JourneysStore } from '../journeys.store';
import { Journey, JourneyInstanceRule } from '@observability-ui/core';
import { ConfirmDialogComponent } from '@observability-ui/ui';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'shell-journey-settings',
  templateUrl: './journey-settings.component.html',
  styleUrls: [ './journey-settings.component.scss' ]
})
export class JourneySettingsComponent extends CoreComponent {
  journey$ = this.store.selected$.pipe(
    tap((journey) => {
      this.form.patchValue({
        id: journey?.id,
        name: journey?.name,
        description: journey?.description,
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

  form = new TypedFormGroup<{
    id: string;
    name: string;
    description: string;
    instance_rules: JourneyInstanceRule[]
    payload_instance_conditions: JourneyInstanceRule[],
  }>({
    id: new TypedFormControl<string>(),
    name: new TypedFormControl<string>(''),
    description: new TypedFormControl<string>(''),
    instance_rules: new TypedFormControl([]),
    payload_instance_conditions: new TypedFormControl([]),
  });

  constructor(
    private store: JourneysStore,
    private dialog: MatDialog,
    private router: Router,
    private route: ActivatedRoute,
  ) {
    super();
  }

  saveInfo(original: Journey): void {
    this.store.dispatch('updateOne', {
      ...omit(this.form.value, [ 'payload_instance_conditions' ]),
      instance_rules: (original.instance_rules ?? []),
    });
  }

  cancelInfoChanges(original: Journey): void {
    this.form.patchValue({ name: original.name, description: original.description });
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
