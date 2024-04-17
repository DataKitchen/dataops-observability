import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'alert',
  template: `
    <div class="alert {{type}}">
      <mat-icon>{{iconMapping[type]}}</mat-icon>
      <ng-content></ng-content>
    </div>
  `,
  styleUrls: [ 'alert.component.scss' ],
  standalone: true,
  imports: [ MatIconModule ]
})

export class AlertComponent {
  @Input() type: 'error' | 'info' | 'success' | 'tips' | 'warning' = 'warning';

  iconMapping = {
    error: 'error',
    warning: 'warning',
    info: 'info',
    tips: 'lightbulb',
    success: 'check_circle'
  };
}
