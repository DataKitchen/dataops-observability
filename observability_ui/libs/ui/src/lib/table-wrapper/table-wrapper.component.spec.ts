import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyTable as MatTable, MatLegacyTableModule as  MatTableModule } from '@angular/material/legacy-table';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { Component, DebugElement, ViewChild } from '@angular/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { ReactiveFormsModule } from '@angular/forms';
import { MatSortModule } from '@angular/material/sort';
import { By } from '@angular/platform-browser';
import { BehaviorSubject } from 'rxjs';
import { CdkDrag } from '@angular/cdk/drag-drop';
import { RouterTestingModule } from '@angular/router/testing';
import { ActivatedRoute } from '@angular/router';
import { OverlayModule } from '@angular/cdk/overlay';
import { TableWrapperComponent } from './table-wrapper.component';
import { Mocked, MockService } from '@datakitchen/ngx-toolkit';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';
import { MockComponent } from '@datakitchen/ngx-toolkit';
import { faker } from '@faker-js/faker';
import { TranslatePipe } from '@observability-ui/translate';
import { MockPipe } from 'ng-mocks';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { DkTooltipModule } from '../dk-tooltip';
import { BindQueryParamsModule } from '../directives';
import { DragDisabledDirective } from './drag-disabled.directive';
import { ToggleDisabledDirective } from './toggle-disabled.directive';
import { SortDisabledDirective } from './sort-disabled.directive';
import { HeaderLabelDirective } from './header-label.directive';
import { MatLegacyProgressBarModule as MatProgressBarModule } from '@angular/material/legacy-progress-bar';
import spyOn = jest.spyOn;

describe('table-wrapper', () => {

  @Component({
    template: `
      <table-wrapper
        [items]="items"
        [total]="total"
        [columns]="visibleColumns"
        [loading]="loading$ | async"
        entity="people"
        (tableChange)="tableChange($any($event))"
      >

        <ng-container matColumnDef="name" sortDisabled>
          <ng-container *matHeaderCellDef>
                        <span headerLabel="name">
                            Name
                        </span>
            <mat-icon>help</mat-icon>
          </ng-container>
          <ng-container *matCellDef="let user">{{user.name}}</ng-container>
        </ng-container>


        <ng-container matColumnDef="age">
          <ng-container *matHeaderCellDef>Age</ng-container>
          <ng-container *matCellDef="let user">{{user.age}}</ng-container>
        </ng-container>


        <ng-container matColumnDef="surname" dragDisabled>
          <ng-container *matHeaderCellDef>Last Name</ng-container>
          <ng-container *matCellDef="let user">{{user.vehicle}}</ng-container>
        </ng-container>

        <ng-container matColumnDef="vehicle" toggleDisabled>
          <ng-container *matHeaderCellDef>Car</ng-container>
          <ng-container *matCellDef="let user">{{user.vehicle}}</ng-container>
        </ng-container>


      </table-wrapper>
    `
  })
  class TestComponent {
    @ViewChild(TableWrapperComponent)
    table: TableWrapperComponent;

    items: Array<{ id: number; name: string; surname: string; vehicle: string }> = [];
    total: number = 0;
    visibleColumns = [ 'id', 'name', {name: 'age', visible: false}, 'surname', 'vehicle' ];
    loading$ = new BehaviorSubject(false);

    tableChange = jest.fn();
  }


  let tableWrapperComponent: TableWrapperComponent;
  let fixture: ComponentFixture<TestComponent>;
  let de: DebugElement;
  let component: TestComponent;
  let storageService: Mocked<StorageService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatTableModule,
        MatPaginatorModule,
        NoopAnimationsModule,
        ReactiveFormsModule,
        MatSortModule,
        RouterTestingModule,
        OverlayModule,
        MatFormFieldModule,
        MatInputModule,
        DkTooltipModule,
        BindQueryParamsModule,
        MatProgressBarModule,
      ],
      declarations: [
        CdkDrag,
        TestComponent,
        TableWrapperComponent,
        MockComponent({
          selector: 'mat-checkbox',
          inputs: [ 'checked', 'indeterminate', 'disabled' ],
        }),
        MockComponent({
          selector: 'mat-icon',
        }),
        MockComponent({
          selector: 'mat-spinner'
        }),
        MockComponent({
          selector: 'mat-divider',
        }),
        MockPipe(TranslatePipe),
        DragDisabledDirective,
        ToggleDisabledDirective,
        SortDisabledDirective,
        HeaderLabelDirective,
      ],
      providers: [
        {
          provide: ParameterService,
          useClass: MockService(ParameterService)(),
        },
        {
          provide: StorageService,
          useClass: MockService(StorageService)(),
        },
        {
          provide: ActivatedRoute,
          useValue: {
            snapshot: {
              url: [ 'table-used-in-here' ]
            }
          },
        },
      ]
    }).compileComponents();


    const parameterService: Mocked<ParameterService> = TestBed.inject(ParameterService) as Mocked<ParameterService>;
    parameterService.getQueryParams.mockReturnValue({
      pageIndex: 0,
      pageSize: 10,
    });

    storageService = TestBed.inject(StorageService) as Mocked<StorageService>;

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    de = fixture.debugElement;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


  describe('init table', () => {
    beforeEach(() => {
      fixture.detectChanges();
      tableWrapperComponent = component.table;
    });

    describe('table with data', () => {

      beforeEach(() => {
        const users: Array<{ id: number; name: string; age: string; surname: string; vehicle: string }> = [];

        for (let i = 0; i < 10; i++) {
          users.push({
            id: i * 10,
            name: faker.person.firstName(),
            surname: faker.person.lastName(),
            vehicle: faker.vehicle.vehicle(),
            age: faker.string.numeric(),
          });
        }

        component.items = users;

        fixture.detectChanges();
      });

      it('should show the table with items', () => {

        const table = de.query(By.directive(MatTable));
        expect(table).toBeTruthy();
        expect(table.queryAll(By.css('mat-row')).length).toEqual(10);
        expect(table.nativeElement.textContent).toContain('Name');

        // this column is toggled off
        expect(table.nativeElement.textContent).not.toContain('Age');

        expect(table.nativeElement.textContent).toContain('Last Name');
        expect(table.nativeElement.textContent).toContain('Car');
      });

      describe('#masterToggle', () => {

        it('should select/deselect items', () => {
          tableWrapperComponent.masterToggle();
          expect(tableWrapperComponent.selection.selected.length).toEqual(10);

          fixture.detectChanges();

          tableWrapperComponent.masterToggle();

          expect(tableWrapperComponent.selection.selected.length).toEqual(0);
        });

      });

      describe('sortable headers', () => {
        it('should have all headers sortable except for the one with the directive `sortDisabled`', async () => {
          const table = de.query(By.directive(MatTable));

          const idHeader = table.query(By.css('mat-header-cell.mat-column-id'));
          idHeader.nativeElement.click();
          fixture.detectChanges();
          await fixture.whenStable();
          expect(component.tableChange).toHaveBeenCalledWith(expect.objectContaining({
            sort: {
              active: 'id',
              direction: 'asc',
            }
          }));

          component.tableChange.mockReset();

          const nameHeader = table.query(By.css('mat-header-cell.mat-column-name'));
          nameHeader.nativeElement.click();
          fixture.detectChanges();
          await fixture.whenStable();
          expect(component.tableChange).not.toHaveBeenCalled();

          component.tableChange.mockReset();

          const vehicleHeader = table.query(By.css('mat-header-cell.mat-column-vehicle'));
          vehicleHeader.nativeElement.click();
          fixture.detectChanges();
          await fixture.whenStable();
          expect(component.tableChange).toHaveBeenCalledWith(expect.objectContaining({
            sort: {
              active: 'vehicle',
              direction: 'asc',
            }
          }));

        });
      });

      describe('draggable columns', () => {

        it('should have all column draggable except for the selection one', () => {
          // please note here we're only checking that the cdkdrag attribute in on the column's headers

          component.visibleColumns.forEach((c) => {
            const name = typeof c === 'string' ? c : c.name;
            const visible = typeof c === 'string' ? true : c.visible;

            if (visible) {
              // not visible columns cannot be picked up by de.query

              const column = de.query(By.css(`mat-header-cell.mat-column-${name}`));

              if (name === 'select') {
                expect('cdkdrag' in column.nativeElement.attributes).toBeFalsy();
              } else {
                expect('cdkdrag' in column.nativeElement.attributes).toBeTruthy();
              }
            }

          });
        });

        it('should disable drag on column with `dragDisabled` directive', () => {
          // please note here we're only checking that the cdk-drag-disabled class on the column's headers

          const column = de.query(By.css('mat-header-cell.mat-column-surname'));
          expect(column.nativeElement.classList.contains('cdk-drag-disabled')).toBeTruthy();
        });

        it('should be able to drag n drop a column', () => {
          const expected = [
            {name: 'select', visible: true},
            {name: 'name', visible: true},
            {name: 'id', visible: true},
            {name: 'age', visible: false},
            {name: 'surname', visible: true},
            {name: 'vehicle', visible: true},
          ];
          tableWrapperComponent.dropListDropped({previousIndex: 0, currentIndex: 1});
          fixture.detectChanges();
          expect(tableWrapperComponent.tableColumns$.value).toEqual(expected);
        });

        it('should not be able to drop on a column that has `dragDisabled` directive', () => {
          const expected = [
            {name: 'select', visible: true},
            {name: 'id', visible: true},
            {name: 'name', visible: true},
            {name: 'age', visible: false},
            {name: 'surname', visible: true},
            {name: 'vehicle', visible: true},
          ];
          tableWrapperComponent.dropListDropped({previousIndex: 0, currentIndex: 2});
          fixture.detectChanges();
          expect(tableWrapperComponent.tableColumns$.value).toEqual(expected);
        });


        // this is problematic. When dropping around a column set to be non-draggable strange things can happen
        // and the non-draggable column can end up at the beginning of the table without the possibility to move it
        // away from there. Not sure if we want to cover this case or just warn the devs about this issue.
        // Leave this tests as skipped for now. Open to future discussions about this problem.
        xdescribe('move a column onto another while there is a non-draggable column in the middle', () => {

          it('should swap the two columns', () => {
            // here we are dropping `vehicle` on `name` while `surname` is not draggable
            // the effect that we want to achieve is to swap the two columns so that `surname` doesn't move

            tableWrapperComponent.dropListDropped({previousIndex: 3, currentIndex: 1,});

            fixture.detectChanges();

            expect(tableWrapperComponent.tableColumns$.value).toEqual([
              {name: 'select', visible: true},
              {name: 'id', visible: true},
              {name: 'vehicle', visible: true},
              {name: 'surname', visible: true},
              {name: 'name', visible: true},
            ]);
          });
        });

        describe('drag and drop with an hidden column', () => {

          beforeEach(async () => {
            tableWrapperComponent.toggleColumnVisibility(tableWrapperComponent.tableColumns$.value[2]);
            fixture.detectChanges();
            await fixture.whenStable();
          });

          it('should move columns with an hidden column in between', () => {

            // here we are moving `id` after `vehicle` column while a column in between (`name`) is hidden
            // and `surname` is not draggable

            /*
             *  this table represent what the columns are and what cdk drag and drop actually sees.
             *  0   { name: 'select', visible: true },        -
             *  1   { name: 'id', visible: true },            0
             *  2   { name: 'name', visible: false },         na
             *  3   { name: 'age', visible: false },          na
             *  4   { name: 'surname', visible: true },       1
             *  5   { name: 'vehicle', visible: true },       2
             */

            tableWrapperComponent.dropListDropped({currentIndex: 2, previousIndex: 0});

            fixture.detectChanges();

            expect(tableWrapperComponent.tableColumns$.value).toEqual([
              {name: 'select', visible: true},
              {name: 'name', visible: false},
              {name: 'age', visible: false},
              {name: 'surname', visible: true},
              {name: 'vehicle', visible: true},
              {name: 'id', visible: true},

            ]);
          });

        });

        describe('drag and drop with two hidden column', () => {

          beforeEach(async () => {
            tableWrapperComponent.toggleColumnVisibility(tableWrapperComponent.tableColumns$.value[2]);
            tableWrapperComponent.toggleColumnVisibility(tableWrapperComponent.tableColumns$.value[4]);
            fixture.detectChanges();
            await fixture.whenStable();
          });

          it('should move a column while there are more hidden', () => {
            // here we are moving `vehicle` before `id` while `name` and `surname` are hidden

            /*
             *  this table represent what the columns are and what cdk drag and drop actually sees.
             *
             *   0   { name: 'select', visible: true },        -
             *   1   { name: 'id', visible: true },            0
             *   2   { name: 'name', visible: false },         na
             *   3   { name: 'age', visible: false },          na
             *   4   { name: 'surname', visible: false },      na
             *   5   { name: 'vehicle', visible: true },       1
             */

            tableWrapperComponent.dropListDropped({previousIndex: 1, currentIndex: 0});

            fixture.detectChanges();

            expect(tableWrapperComponent.tableColumns$.value).toEqual([
              {name: 'select', visible: true},
              {name: 'vehicle', visible: true},
              {name: 'id', visible: true},
              {name: 'name', visible: false},
              {name: 'age', visible: false},
              {name: 'surname', visible: false},
            ]);
          });
        });

      });

      it('should trigger a reload', async () => {
        tableWrapperComponent.onReload();
        fixture.detectChanges();
        await fixture.whenStable();
        expect(component.tableChange).toHaveBeenCalled();
      });

      describe('#toggleColumnVisibility', () => {

        it('should toggle a column\'s visibility', () => {
          spyOn(tableWrapperComponent.tableColumns$, 'next');

          // angular passes a reference to the toggled column so that it's visibility is changed in place
          // no need to replace the column in  `tableColumns$` but for testing purpose we need to actually
          // pass that same ref.
          tableWrapperComponent.toggleColumnVisibility(tableWrapperComponent.tableColumns$.value[2]);
          expect(tableWrapperComponent.tableColumns$.next).toHaveBeenCalledWith(expect.arrayContaining(
            [{name: 'name', visible: false}],
          ));
        });

        it('should have toggle disabled on columns with `toggleDisabled` directive', () => {
          expect(tableWrapperComponent.hasToggleDisabled('vehicle')).toBeTruthy();
        });
      });

    });

  });

  describe('table columns stored in local storage do not match the given columns', () => {

    beforeEach(() => {

      storageService.getStorage.mockReturnValue([
        {name: 'name', visible: true},
        {name: 'surname', visible: false},
      ]);
      fixture.detectChanges();
      tableWrapperComponent = component.table;
    });

    it('should have reset all columns', () => {
      expect(tableWrapperComponent.tableColumns$.value).toEqual([
        {name: 'select', visible: true},
        {name: 'id', visible: true},
        {name: 'name', visible: true},
        {name: 'age', visible: false},
        {name: 'surname', visible: true},
        {name: 'vehicle', visible: true},
      ]);
    });
  });

});
