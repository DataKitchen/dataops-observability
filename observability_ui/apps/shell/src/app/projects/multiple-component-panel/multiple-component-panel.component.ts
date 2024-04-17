import { Component } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FlexModule } from '@angular/flex-layout';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatExpansionModule } from '@angular/material/expansion';
import { TranslationModule } from '@observability-ui/translate';
import { AsyncPipe, JsonPipe, NgFor, NgIf } from '@angular/common';
import { ToolSelectorComponent } from '../integrations/tool-selector/tool-selector.component';
import { AbstractControl, ReactiveFormsModule } from '@angular/forms';
import { ComponentStore } from '../components/components.store';
import { filter, map, take, tap } from 'rxjs';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { ComponentType, Schedule } from '@observability-ui/core';
import { omit, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { EditExpectedScheduleComponent } from '../edit-expected-schedule/edit-expected-schedule.component';
import { EditExpectedArrivalWindowComponent } from '../edit-expected-arrival-window/edit-expected-arrival-window.component';
import { MatLegacyCheckboxModule } from '@angular/material/legacy-checkbox';
import { ComponentIconComponent } from '../components/component-icon/component-icon.component';
import { TruncateModule } from '@observability-ui/ui';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';

@Component({
  selector: 'shell-multiple-component-panel',
  templateUrl: 'multiple-component-panel.component.html',
  standalone: true,
  imports: [
    RouterLink,
    FlexModule,
    MatIconModule,
    MatLegacyButtonModule,
    MatExpansionModule,
    TranslationModule,
    AsyncPipe,
    ToolSelectorComponent,
    ReactiveFormsModule,
    JsonPipe,
    EditExpectedScheduleComponent,
    NgIf,
    EditExpectedArrivalWindowComponent,
    MatLegacyCheckboxModule,
    ComponentIconComponent,
    TruncateModule,
    NgFor,
    MatLegacyProgressSpinnerModule
  ],
  styleUrls: [ 'multiple-component-panel.component.scss' ]
})
export class MultipleComponentPanelComponent {
  canEditArrivalWindow!: boolean;
  canEditSchedule!: boolean;

  loading = toSignal(this.store.getLoadingFor('updateOne'));

  components = toSignal(this.store.allComponents$.pipe(
    take(1),
    map((components) => {
      const ids = this.route.snapshot.params['ids'].split(',');
      const filteredComponents = components.filter((comp) => ids.includes(comp.id));

      this.canEditArrivalWindow = filteredComponents.find((comp) => comp.type === ComponentType.Dataset) !== undefined;
      this.canEditSchedule = filteredComponents.find((comp) => comp.type === ComponentType.BatchPipeline) !== undefined;

      return filteredComponents;
    })
  ));

  form = new TypedFormGroup<{
    expectedArrivalWindow: Schedule,
    startsAt: Schedule,
    endsAt: Schedule,
    tool: string,
    editTool: boolean,
    editArrival: boolean,
    editSchedule: boolean
  }>({
    tool: new TypedFormControl<string>(),
    expectedArrivalWindow: new TypedFormControl<Schedule>(undefined, [ this.validateExpectedArrivalWindow.bind(this) ]),
    startsAt: new TypedFormControl<Schedule>(undefined, [ this.validateStartsAt.bind(this) ]),
    endsAt: new TypedFormControl<Schedule>(),
    editTool: new TypedFormControl<boolean>(false),
    editSchedule: new TypedFormControl<boolean>(false),
    editArrival: new TypedFormControl<boolean>(false)
  });

  constructor(private route: ActivatedRoute, private router: Router, private store: ComponentStore) {
    this.store.allComponents$.pipe(
      take(1),
      tap((components) => {
        if (!components || components.length === 0) {
          this.router.navigate([ '../..' ], { relativeTo: this.route });
        }
      })
    ).subscribe();

    this.store.loading$.pipe(
      filter(({ code }) => code === 'updateOne'),
      filter(({ status }) => status === false),
      tap(() => this.router.navigate([ '../..' ], { relativeTo: this.route })),
      takeUntilDestroyed(),
    ).subscribe();
  }

  save() {
    const { editTool, editArrival, editSchedule } = this.form.value;

    this.components().forEach((component) => {
      this.store.dispatch('updateOne', {
        ...component,
        tool: this.form.value.tool && editTool ? this.form.value.tool : component.tool
      }, omit(this.form.value, [ 'tool', 'editTool', 'editArrival', 'editSchedule' ]), editSchedule, editArrival);
    });
  }

  private validateExpectedArrivalWindow(fc: AbstractControl<Schedule>): { [key: string]: boolean } | null {

    if (!this.form) {
      return null;
    }

    const { margin, schedule } = fc.value || {};

    // reset errors
    this.form.setErrors(null);

    let error = null;

    if (margin && !schedule) {
      // missing schedule
      error = { schedule: true };
    }

    if (!margin && schedule) {
      error = { margin: true };
    }

    if (schedule && margin < 300) {
      error = { min_margin: true };
    }

    this.form.setErrors(error);

    return error;
  }

  private validateStartsAt(fc: AbstractControl<Schedule>): { [key: string]: boolean } | null {

    if (!this.form) {
      return null;
    }

    const { margin, schedule } = fc.value || {};

    // reset errors
    this.form.setErrors(null);

    let error = null;

    if (margin && !schedule) {
      // missing schedule
      error = { schedule: true };
    }

    if (!margin && schedule) {
      error = { margin: true };
    }

    this.form.setErrors(error);

    return error;
  }
}
