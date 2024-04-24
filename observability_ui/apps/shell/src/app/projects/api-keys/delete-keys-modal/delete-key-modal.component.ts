import { Component, Inject } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialogModule, MatLegacyDialogRef } from '@angular/material/legacy-dialog';
import { APIKeysStore } from '../api-keys.store';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { filter, tap } from 'rxjs';

@Component({
  selector: 'shell-delete-key-modal',
  standalone: true,
  imports: [
    MatIconModule,
    MatLegacyButtonModule,
    MatLegacyDialogModule
  ],
  template: `
    <div mat-dialog-title>
      <span>Delete API Keys</span>
      <span class="fx-flex"></span>
      <button mat-icon-button
        mat-dialog-close>
        <mat-icon>close</mat-icon>
      </button>
    </div>
    <div mat-dialog-content>
      <div class="pb-3">
        <div class="mb-2">
          Are you sure you want to delete these API keys? This operation could affect the existing agents.
        </div>
      </div>
    </div>
    <div mat-dialog-actions>
      <button mat-flat-button
        [disabled]="deleting()"
        mat-dialog-close>Cancel
      </button>
      <button color="warn"
        (click)="deleteSelected()"
        [disabled]="deleting()"
        mat-flat-button>Delete</button>
    </div>
  `
})

export class DeleteKeyModalComponent {
  deleting = toSignal(this.store.getLoadingFor('deleteOne'));

  constructor(@Inject(MAT_LEGACY_DIALOG_DATA) public data: {
    ids: string[]
  }, private store: APIKeysStore, private ref: MatLegacyDialogRef<DeleteKeyModalComponent>) {
    this.store.loading$.pipe(
      takeUntilDestroyed(),
      filter(({code}) => code === 'deleteOne'),
      filter(({status}) => status === false),
      tap(() => {
        this.ref.close();
      })
    ).subscribe();
  }

  deleteSelected() {
    this.data.ids.forEach((id) => {
      this.store.dispatch('deleteOne', id);
    });
  }
}
