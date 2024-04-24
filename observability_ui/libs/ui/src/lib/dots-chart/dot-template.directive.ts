/* istanbul ignore file */

import { Directive, Input, TemplateRef } from '@angular/core';

@Directive({
  selector: '[dotTpl]',
  standalone: true,
})
export class DotTemplateDirective {
  @Input('dotTpl') value!: object;

  constructor(public template: TemplateRef<any>) {}
}
