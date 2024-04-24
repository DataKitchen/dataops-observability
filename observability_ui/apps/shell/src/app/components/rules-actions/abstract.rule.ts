import { Directive, TemplateRef, ViewChild } from '@angular/core';
import { Rule } from './rule.model';
import { AbstractTemplating } from './abstract-templating.directive';

@Directive()
export abstract class AbstractRule extends AbstractTemplating {
  @ViewChild('advancedOptions') advancedOptions: TemplateRef<any>;

  /**
   * Whether the part that says "For any component in pipeline", displayed
   * along the rules, should be visible or not.
   */
  static showComponentSelection: boolean = true;

  version = 'simple_v1';


  toJSON(): Pick<Rule, 'rule_data'|'rule_schema'> {
    return {
      rule_data: {
        when: 'all',
        conditions: [
          {
            [this.type]: this.form.value,
          }
        ]
      },
      rule_schema: this.version
    };
  }


  hasAdvancedOptions(): boolean {
    return this.advancedOptions !== undefined;
  }

  getValue(): any {
    return this.form.value;
  }
}
