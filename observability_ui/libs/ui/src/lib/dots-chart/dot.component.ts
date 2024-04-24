import { Component, HostBinding, Input } from '@angular/core';

@Component({
  selector: 'dot',
  template: ``,
  styleUrls: ['dot.component.scss'],
  standalone: true,
})
export class DotComponent {
  @HostBinding('class') @Input() status!: 'ACTIVE' | 'COMPLETED' | 'WARNING' | 'ERROR' | 'UPCOMING';
  @HostBinding('class.has-runs') @Input() hasRuns!: boolean;
}
