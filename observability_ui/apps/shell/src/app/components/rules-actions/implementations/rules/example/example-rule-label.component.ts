import { Component } from '@angular/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'label-example-rule',
  template: `<span class="label">🌈 example rule label 🦄</span>`,
  standalone: true,
  styles: [ `
    .label {
        text-transform: capitalize;
    }
  ` ],
})
export class ExampleRuleLabelComponent {
}
