import { Component, effect, Inject } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatIconModule } from '@angular/material/icon';
import { ComponentUI } from '../components.store';
import { MatExpansionModule } from '@angular/material/expansion';
import { ComponentIconComponent } from '../component-icon/component-icon.component';
import { toSignal } from '@angular/core/rxjs-interop';
import { JourneysStore } from '../../journeys/journeys.store';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { TextFieldModule } from '@observability-ui/ui';
import { filter } from 'rxjs';
import { Router } from '@angular/router';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef } from '@angular/material/legacy-dialog';

@Component({
  selector: 'shell-multiple-journey-dialog',
  template: `
    <div mat-dialog-title>
      <span>Add components to new Journey</span>
      <span class="fx-flex"></span>
      <button mat-icon-button
        mat-dialog-close>
        <mat-icon>close</mat-icon>
      </button>
    </div>
    <div mat-dialog-content>
      <div class="mb-2">
        <text-field label="Name"
          placeholder="Name"
          [formControl]="form.controls.name"></text-field>
      </div>
      <div class="mb-2">
        <text-field label="Description"
          placeholder="Description"
          [formControl]="form.controls.description"></text-field>
      </div>
      <mat-expansion-panel class="mat-elevation-z0">
        <mat-expansion-panel-header>
          <mat-panel-title>These components are going to be added to the new journey</mat-panel-title>
        </mat-expansion-panel-header>

        <div class="expansion-container">
          <div class="pt-2 pb-2 flex-row detail-container"
            *ngFor="let component of data.components">
            <component-icon [type]="component.type"
              [tool]="component.tool"></component-icon>
            <span class="ml-2">{{component.display_name}}</span>
          </div>
        </div>
      </mat-expansion-panel>
    </div>
    <div mat-dialog-actions>
      <button mat-flat-button
        [disabled]="loading()"
        mat-dialog-close>Cancel
      </button>
      <button color="primary"
        (click)="createJourney()"
        [disabled]="!form.valid || loading()"
        mat-flat-button>{{'Create'}}</button>
    </div>
  `,
  imports: [
    NgIf,
    NgFor,
    MatLegacyButtonModule,
    MatLegacyDialogModule,
    MatIconModule,
    MatExpansionModule,
    ComponentIconComponent,
    MatLegacyProgressSpinnerModule,
    TextFieldModule,
    ReactiveFormsModule
  ],
  standalone: true,
  styleUrls: [ 'multiple-journey-dialog.component.scss' ]
})

export class MultipleJourneyDialogComponent {
  form = new FormGroup({
    name: new FormControl('', Validators.required),
    description: new FormControl('')
  });

  addAction = toSignal(this.store.loading$.pipe(
    filter(({ code }) => code === 'createOne'),
    filter(({ status }) => status === false),
  ));

  journeys = toSignal(this.store.list$);
  loading = toSignal(this.store.getLoadingFor('createOne'));

  constructor(@Inject(MAT_LEGACY_DIALOG_DATA) public data: {
    ids: string[],
    components: ComponentUI[],
    projectId: string
  }, private store: JourneysStore, private dialog: MatLegacyDialogRef<any>, private router: Router) {
    effect(() => {
      if (this.addAction()?.response) {
        this.dialog.close();
        void this.router.navigate([ `projects/${this.data.projectId}/journeys/${this.addAction().response.id}` ]);
      }
    });
  }

  createJourney() {
    this.store.dispatch('createOne', {
      name: this.form.value.name,
      description: this.form.value.description,
      project_id: this.data.projectId,
      instance_rules: [],
      components: this.data.components.map(x => x.id)
    });
  }
}
