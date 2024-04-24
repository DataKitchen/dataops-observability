import { Component, Input } from '@angular/core';
import { NgClass, NgStyle } from '@angular/common';

@Component({
  selector: 'shell-summary-item',
  templateUrl: 'summary-item.component.html',
  styleUrls: [ 'summary-item.component.scss' ],
  imports: [
    NgStyle,
    NgClass
  ],
  standalone: true
})

export class SummaryItemComponent {
  @Input() count: number;
  @Input() color: string;
  @Input() label: string;
}
