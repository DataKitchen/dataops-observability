import { Component, Inject } from '@angular/core';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogRef as MatDialogRef } from '@angular/material/legacy-dialog';

@Component({
  selector: 'shell-delete-component-dialog',
  template: `
    <h1 mat-dialog-title>{{'componentsPanel.deleteComponent' | translate}}</h1>
    <div mat-dialog-content>
      {{'componentsPanel.confirmDelete' | translate}}
    </div>
    <div mat-dialog-actions>
      <button mat-button
        (click)="dialogRef.close()">{{'componentsPanel.cancel' | translate}}
      </button>
      <button mat-button
        color="warn"
        [mat-dialog-close]="data.id">{{'componentsPanel.delete' | translate}}
      </button>
    </div>
  `
})

export class DeleteComponentDialogComponent {
  constructor(
    public dialogRef: MatDialogRef<DeleteComponentDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { id: string },) {
  }
}
