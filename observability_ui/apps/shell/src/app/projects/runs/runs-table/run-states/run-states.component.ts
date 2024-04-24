import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { Run, RunProcessedStatus } from '@observability-ui/core';

@Component({
  selector: 'shell-run-states',
  templateUrl: './run-states.component.html',
  styleUrls: [ './run-states.component.scss' ]
})
export class RunStatesComponent implements OnChanges {
  @Input() run: Partial<Run> & Pick<Run, 'status'>;

  hasWarnings: boolean;
  state: RunProcessedStatus;
  RunProcessedStatus = RunProcessedStatus;

  ngOnChanges(changes: SimpleChanges) {
    if (changes['run']) {
      this.state = this.getStatePriority();
      this.hasWarnings = this.state === RunProcessedStatus.CompletedWithWarnings;
    }
  }

  /**
   * @deprecated until completely phased out from the API
   */
  private getStatePriority(): RunProcessedStatus {
    if (this.run.status) {
      return this.run.status;
    }

    return RunProcessedStatus.Completed;
  }
}
