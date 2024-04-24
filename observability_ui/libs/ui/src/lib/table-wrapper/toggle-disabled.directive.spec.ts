import { ToggleDisabledDirective } from './toggle-disabled.directive';
import { MatLegacyColumnDef } from '@angular/material/legacy-table';

describe('toggle-disabled.directive', () => {

  let directive: ToggleDisabledDirective;

  beforeEach(() => {
    const column = new MatLegacyColumnDef();
    column.name = 'name';
    directive = new ToggleDisabledDirective(column);
  });

  it('should create', () => {
    expect(directive).toBeTruthy();
  });

  it('should set the column\' name', () => {
    directive.ngOnInit();
    expect(directive.columnName).toEqual('name');
  });

  it('should be disabled by default', () => {
    // when a directive is used without any value angular defaults to `''` (empty string) regardless of the type of the input
    // @ts-ignore
    directive.disabled = '';
    directive.ngOnInit();

    expect(directive.disabled).toBeTruthy();
  });

  it('should set given state', () => {
    directive.disabled = false;
    directive.ngOnInit();
    expect(directive.disabled).toBeFalsy();

    directive.disabled = true;
    directive.ngOnInit();
    expect(directive.disabled).toBeTruthy();
  });
});
