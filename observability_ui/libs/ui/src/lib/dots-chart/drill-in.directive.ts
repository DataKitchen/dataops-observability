/* istanbul ignore file */

import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[drillInTemplate]',
  standalone: true,
})
export class DrillInTemplateDirective {
  constructor(public template: TemplateRef<any>) {}
}
