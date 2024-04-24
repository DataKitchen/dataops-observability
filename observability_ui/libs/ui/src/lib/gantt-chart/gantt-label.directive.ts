/* istanbul ignore file */

import { Directive, TemplateRef } from '@angular/core';

@Directive({
  selector: '[ganttLabel]',
})
export class GanttLabelDirective {
  constructor(
    public template: TemplateRef<any>,
  ) {}
}
