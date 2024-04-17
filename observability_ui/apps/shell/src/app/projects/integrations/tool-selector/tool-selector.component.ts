import { Component, inject, Input, OnInit, Optional, Self } from '@angular/core';
import { TypedFormControl } from '@datakitchen/ngx-toolkit';
import { map, startWith } from 'rxjs';
import { AbstractField } from '@observability-ui/ui';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule } from '@angular/material/legacy-input';
import { NgControl, ReactiveFormsModule } from '@angular/forms';
import { MatLegacyAutocompleteModule } from '@angular/material/legacy-autocomplete';
import { AsyncPipe, LowerCasePipe, NgForOf, NgIf, TitleCasePipe } from '@angular/common';
import { GetToolClassPipe } from './get-tool-class.pipe';
import { ComponentIconComponent } from '../../components/component-icon/component-icon.component';
import { EXTRA_TOOL_ICONS, INTEGRATION_TOOLS } from '../integrations.model';
import { tap } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({
  selector: 'shell-tool-selector',
  standalone: true,
  template: `

    <ng-container *ngIf="editing; else display">
      <mat-form-field>
        <mat-label>Tool</mat-label>

        <input type="text"
          placeholder="Enter a name or select a tool from the list"
          aria-label="Tool"
          matInput
          [formControl]="toolFC"
          [matAutocomplete]="auto">

        <mat-autocomplete #auto="matAutocomplete">
          <mat-option *ngFor="let option of filteredOptions$ | async"
            [value]="option._displayName">
            <div class="fx-row fx-align-baseline">
              <component-icon
                [tool]="option._name"
              ></component-icon>
              {{option._displayName}}
            </div>
          </mat-option>
        </mat-autocomplete>
      </mat-form-field>

    </ng-container>

    <ng-template #display>


      <div *ngIf="tool !== null"
        class="fx-row fx-align-flex-center">
        <ng-container *ngIf="tool | getToolClass  as component; else custom">

          <component-icon class="mr-2"
            [tool]="component._name.toUpperCase()"></component-icon>
          {{component._displayName}}
        </ng-container>

        <ng-template #custom>
          {{tool}}
        </ng-template>
      </div>

    </ng-template>

  `,
  imports: [
    MatLegacyFormFieldModule,
    MatLegacyInputModule,
    ReactiveFormsModule,
    MatLegacyAutocompleteModule,
    AsyncPipe,
    LowerCasePipe,
    GetToolClassPipe,
    ComponentIconComponent,
    NgIf,
    NgForOf,
    TitleCasePipe,
  ],
  providers: [
    GetToolClassPipe,
  ],
  styles: [ `
    :host {
      display: flex;
      flex-direction: row;
    }

    :host ::ng-deep .mat-form-field, :host ::ng-deep .mat-form-field-wrapper {
      display: flex;
      flex-direction: row;
      flex-grow: 1;
    }

  ` ]
})
export class ToolSelectorComponent extends AbstractField implements OnInit {
  @Input() editing: boolean = false;
  @Input() tool: string;

  integrations = inject(INTEGRATION_TOOLS);
  extraTools = inject(EXTRA_TOOL_ICONS);

  allTools = [ ...this.integrations, ...this.extraTools ].sort((a, b) => a._displayName.localeCompare(b._displayName));

  toolFC = new TypedFormControl<string>();

  filteredOptions$ = this.toolFC.valueChanges.pipe(
    startWith(''),
    map((search) => {
      if (search) {
        return this.allTools.filter(({ _displayName }) => {
          return _displayName.toLowerCase().includes(search.toLowerCase());
        });
      } else {
        return this.allTools;
      }
    }),
  );
  private internalChange: boolean;
  private externalChange: boolean;

  constructor(
    private getClassTool: GetToolClassPipe,
    @Self() @Optional() override ngControl?: NgControl,
  ) {
    super(ngControl);

    this.toolFC.valueChanges.pipe(
      map((displayName) => {
        const klass = this.allTools.find((i) => i._displayName === displayName);
        return klass?._name ?? displayName;
      }),
      tap((displayName) => {

        if (!this.externalChange) {

          this.internalChange = true;
          this.control.setValue(displayName || null);
        } else {
          this.externalChange = false;
        }
      }),
      takeUntilDestroyed(),
    ).subscribe();
  }

  override writeValue(value: any) {

    if (!this.internalChange) {
      this.externalChange = true;
      const klass = this.getClassTool.transform(value);
      this.toolFC.patchValue(klass?._displayName ?? value);
    } else {
      this.internalChange = false;
    }

  }



}
