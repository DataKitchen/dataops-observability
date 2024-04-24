import { Component, computed, Input, signal } from '@angular/core';
import { RunAlert, RunAlertType } from '@observability-ui/core';

@Component({
  selector: 'shell-run-time',
  templateUrl: './run-time.component.html',
  styleUrls: ['./run-time.component.scss'],
})
export class RunTimeComponent {

  @Input() set actual(value: string) {
    this._actual.set(value);
  }
  @Input() expected: string | undefined;
  @Input() alerts: RunAlert[] | undefined;
  @Input() alertType: RunAlertType | undefined;

  @Input() dateFormat: string = 'MMM d, h:mm:ss a';
  @Input() iconLabel: string;

  private _actual = signal<string | null>(null);

  time = computed(() => {
    return this._actual() || this.expected;
  });

  lateness = computed(() => {
    return this.alertType && this.alerts?.find(a => a.type === this.alertType);
  });
}
