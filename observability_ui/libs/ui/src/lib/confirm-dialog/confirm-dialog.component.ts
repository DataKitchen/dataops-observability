import { Component, Inject } from '@angular/core';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { NgIf } from '@angular/common';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'confirm-dialog',
  template: `
    <div mat-dialog-title>
      {{data.title}}
      <span class="fx-flex"></span>
      <button mat-icon-button
        mat-dialog-close>
        <mat-icon>close</mat-icon>
      </button>
    </div>
    <div mat-dialog-content>{{data.message}}</div>
    <div mat-dialog-actions>
      <button mat-flat-button
        mat-dialog-close>{{data.cancelLabel || 'Cancel'}}</button>
      <button color="{{data.confirmButtonColor || 'primary'}}"
        [mat-dialog-close]="data"
        mat-flat-button>{{data.confirmLabel || 'Confirm'}}</button>
    </div>
  `,
  imports: [
    NgIf,
    MatLegacyButtonModule,
    MatDialogModule,
    MatIconModule
  ],
  standalone: true,
  styleUrls: ['confirm-dialog.component.scss']
})

export class ConfirmDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: {
    title: string,
    message: string,
    confirmLabel: string,
    cancelLabel: string,
    confirmButtonColor: string,
  }) {
  }
}
