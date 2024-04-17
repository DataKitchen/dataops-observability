import { MatLegacyColumnDef as MatColumnDef } from '@angular/material/legacy-table';
import { DragDisabledDirective } from './drag-disabled.directive';

describe('drag-disabled.directive', () => {

  let directive: DragDisabledDirective;

  beforeEach(() => {
    const column = new MatColumnDef();
    column.name = 'name';
    directive = new DragDisabledDirective(column);
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
