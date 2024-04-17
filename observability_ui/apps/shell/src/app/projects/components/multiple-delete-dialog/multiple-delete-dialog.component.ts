import { Component, Inject } from '@angular/core';
import { NgFor, NgIf } from '@angular/common';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatIconModule } from '@angular/material/icon';
import { ComponentUI } from '../components.store';
import { MatExpansionModule } from '@angular/material/expansion';
import { ComponentIconComponent } from '../component-icon/component-icon.component';
import { toSignal } from '@angular/core/rxjs-interop';
import { JourneysStore } from '../../journeys/journeys.store';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule } from '@angular/material/legacy-dialog';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'shell-delete-components-dialog',
  template: `
    <div mat-dialog-title>
      <span>Delete Components</span>
      <span class="fx-flex"></span>
      <button mat-icon-button
        mat-dialog-close>
        <mat-icon>close</mat-icon>
      </button>
    </div>
    <div mat-dialog-content>
      <div class="pb-3">
        <div class="mb-2">
          Are you sure you want to delete these components? Any journeys and instances that include
          these components will immediately reflect this change. Click any component to view its related journeys.
        </div>
        <mat-expansion-panel class="mat-elevation-z0">
          <mat-expansion-panel-header>
            <mat-panel-title>These components are going to be deleted</mat-panel-title>
          </mat-expansion-panel-header>

          <div class="expansion-container">
            <div class="pt-2 pb-2 flex-row detail-container"
              *ngFor="let component of data.components">
              <component-icon [type]="component.type"
                [tool]="component.tool"></component-icon>
              <span class="ml-2">{{component.display_name}}</span>
              <span class="fx-flex"></span>
              <button (click)="getJourneysForComponent(component)"
                mat-flat-button>View related journeys
              </button>
            </div>
          </div>
        </mat-expansion-panel>
        <div *ngIf="selectedComponent"
          class="mt-3">
          <mat-expansion-panel class="mat-elevation-z0">
            <mat-expansion-panel-header>
              <mat-panel-title>These journeys will be affected</mat-panel-title>
            </mat-expansion-panel-header>

            <div class="loading-container"
              *ngIf="loading() === true">
              <mat-progress-spinner diameter="20"
                mode="indeterminate"
                color="primary"
              ></mat-progress-spinner>
            </div>

            <ng-container *ngIf="loading() === false">
              <ng-container *ngIf="selectedComponent">
                <div>
                  By deleting component <span class="text--bold-1">{{selectedComponent.display_name}}</span>
                </div>

                <div class="expansion-container">
                  <div class="pt-2 pb-2 flex-row detail-container"
                    *ngFor="let journey of journeys()">
                    <span>{{journey.name}}</span>
                    <a target="_blank"
                      [routerLink]="['projects', this.data.projectId, 'journeys', journey.id]"
                      class="link">
                      <mat-icon class="icon-16">open_in_new</mat-icon>
                    </a>
                  </div>

                  <div class="pt-2 pb-2"
                    *ngIf="journeys().length === 0">
                    This component is not present in any journey
                  </div>
                </div>
              </ng-container>
            </ng-container>

            <ng-container *ngIf="!selectedComponent">
              <span>Select a component to view the related journeys</span>
            </ng-container>
          </mat-expansion-panel>
        </div>
      </div>
    </div>
    <div mat-dialog-actions>
      <button mat-flat-button
        mat-dialog-close>Cancel
      </button>
      <button color="warn"
        [mat-dialog-close]="data"
        mat-flat-button>{{'Delete'}}</button>
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
    RouterModule
  ],
  standalone: true,
  styleUrls: [ 'multiple-delete-dialog.component.scss' ]
})

export class MultipleDeleteDialogComponent {
  selectedComponent!: ComponentUI;

  loading = toSignal(this.store.getLoadingFor('findAll'));
  journeys = toSignal(this.store.list$);

  constructor(@Inject(MAT_LEGACY_DIALOG_DATA) public data: {
    ids: string[],
    components: ComponentUI[],
    projectId: string
  }, private store: JourneysStore) {
  }

  getJourneysForComponent(component: ComponentUI) {
    this.selectedComponent = component;

    this.store.dispatch('findAll', { parentId: this.data.projectId, filters: { component_id: component.id } });
  }
}
