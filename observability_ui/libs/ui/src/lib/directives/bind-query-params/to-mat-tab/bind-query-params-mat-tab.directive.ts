import { Directive, Input } from '@angular/core';
import { MatLegacyTabGroup as MatTabGroup } from '@angular/material/legacy-tabs';
import { Params } from '@angular/router';
import { BindQueryParamsAbstract } from '../bind-query-params.abstract';
import { ParameterService } from '@datakitchen/ngx-toolkit';

@Directive({selector: '[bindQueryParamsMatTab]'})
export class BindQueryParamsMatTabDirective extends BindQueryParamsAbstract {
  @Input('bindQueryParamsMatTab')
  paramName!: string;

  @Input()
  tabNames!: string[];

  constructor(
    override parameterService: ParameterService,
    protected tabGroup: MatTabGroup,
  ) {
    super(parameterService, tabGroup.selectedIndexChange);
  }

  protected setInitialValue(params: Params): void {
    const tab = params[this.paramName] as string;
    const index = (Array.isArray(this.tabNames) ? (this.tabNames.includes(tab) ? this.tabNames.indexOf(tab) : 0) : tab) as number;

    this.tabGroup.selectedIndex = index;
  }

  override parseValuesToParams(values: Params): Params {
    return {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      [this.paramName]: Array.isArray(this.tabNames) ? (this.tabNames[values] || values) : values,
    };
  }
}
