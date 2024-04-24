import { Component, EventEmitter, Input, Output, signal } from '@angular/core';
import { DagOrientation } from '../dag.model';
import { animate, state, style, transition, trigger } from '@angular/animations';

@Component({
  selector: 'dag-actions',
  templateUrl: 'dag-actions.component.html',
  styleUrls: [ 'dag-actions.component.scss' ],
  animations: [
    trigger('openClose', [
      state('opened', style({ width: '100%', display: 'flex' })),
      state('closed', style({ width: '0', overflow: 'hidden' })),
      transition('* => opened', [ animate('300ms') ]),
      transition('* => closed', [ animate('300ms') ]),
    ]),
  ],
})
export class DagActionsComponent {
  @Input() zoom!: number | null;
  @Input() layout!: DagOrientation | null;

  @Input() maxZoom: number = Infinity;
  @Input() minZoom: number = 1;

  @Input() hasLegend: boolean = false;

  @Output() arrange: EventEmitter<DagOrientation> = new EventEmitter();

  @Output() zoomIn: EventEmitter<never> = new EventEmitter<never>();
  @Output() zoomOut: EventEmitter<never> = new EventEmitter<never>();
  @Output() zoomToFit: EventEmitter<never> = new EventEmitter<never>();

  showLegend = signal<boolean>(false);

  readonly DagOrientation = DagOrientation;

  toggleLegend(): void {
    this.showLegend.set(!this.showLegend());
  }
}
