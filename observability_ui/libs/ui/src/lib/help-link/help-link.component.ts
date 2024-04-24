import { Component, Input } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { TranslationModule } from '@observability-ui/translate';
import { NgIf } from '@angular/common';

@Component({
  selector: 'help-link',
  template: `
    <ng-container *ngIf="showLearnMore">Learn more about&nbsp;</ng-container>
    <a [href]="href"
      [attr.target]="target"
      class="link"
      (click)="openPopup($event)">
      <ng-content></ng-content>
      <mat-icon inline>open_in_new</mat-icon>
    </a>
  `,
  styles: [`
    :host {
      display: flex;
      flex-direction: row;
      font-size: 12px;
      color: var(--text-secondary-color);

      :is(a) {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: center;

        :is(mat-icon) {
          width: 13px;
          height: 13px;
          font-size: 13px;
          line-height: 13px;
          margin-left: 2px;
        }
      }
    }
  `],
  standalone: true,
  imports: [
    MatIconModule,
    TranslationModule,
    NgIf
  ],
})
export class HelpLinkComponent {
  @Input() href!: string;
  @Input() target: '_blank' | 'popup' = '_blank';
  @Input() showLearnMore: boolean = true;

  // TODO: Make use of a popup component from this UI library
  openPopup($event: MouseEvent): boolean {
    if (this.target !== 'popup') {
      return true;
    }

    $event.preventDefault();
    $event.stopImmediatePropagation();

    const popup = this.getPopup();
    popup.location.href = this.href;

    (window as any).DatakitchenHelpPopup = popup;

    return false;
  }

  private getPopup(): Window {
    let popup = (window as any).DatakitchenHelpPopup;
    if (popup && popup.closed) {
      popup = (window as any).DatakitchenHelpPopup = undefined;
    }

    return popup ?? window.open('', 'Datakitchen Help', 'height=800,width=700');
  }
}
