import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'selected-actions',
  templateUrl: 'selected-actions.component.html',
  imports: [
    MatLegacyButtonModule,
    MatMenuModule,
    MatIconModule
  ],
  standalone: true,
  styleUrls: [ 'selected-actions.component.scss' ]
})

export class SelectedActionsComponent {
  @Input() elements!: any[];
  @Input() label: string = 'item';
  @Input() hideSelectMenu: boolean = false;

  @Output() clear = new EventEmitter<void>();
  @Output() selectAll = new EventEmitter<void>();

  constructor() {
  }
}
