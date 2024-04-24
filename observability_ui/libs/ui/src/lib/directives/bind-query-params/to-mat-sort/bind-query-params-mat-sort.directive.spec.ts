import { Component, ViewChild } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { MatSort, MatSortModule } from '@angular/material/sort';
import { Mocked, MockService } from '@datakitchen/ngx-toolkit';
import { ParameterService } from '@datakitchen/ngx-toolkit';
import { BindQueryParamsModule } from '../bind-query-params.module';

describe('bindQueryParamsMatSort', () => {

  const sortBy = 'columnX';
  const sortOrder = 'desc';

  @Component({
    selector: 'test-component',
    template: `
      <table matSort
             bindQueryParamsMatSort
             #sort="matSort">
        <tr>
          <th mat-sort-header="columnX">X</th>
          <th mat-sort-header="columnY">Y</th>
        </tr>
      </table>
    `,
  })
  class TestComponent {
    @ViewChild('sort') sort: MatSort;
  }

  let fixture: ComponentFixture<TestComponent>;
  let component: TestComponent;
  let parameterService: Mocked<ParameterService>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSortModule,
        NoopAnimationsModule,
        BindQueryParamsModule,
      ],
      declarations: [
        TestComponent,
      ],
      providers: [
        {provide: ParameterService, useClass: MockService(ParameterService)()},
      ],
    }).compileComponents();

    parameterService = TestBed.inject(ParameterService) as Mocked<ParameterService>;
    parameterService.getQueryParams.mockReturnValue({});

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('setInitialValue()', () => {

    it('should set initial sort values on from query parameters', async () => {
      parameterService.getQueryParams.mockReturnValue({sortBy, sortOrder});
      fixture.detectChanges();
      await fixture.whenStable();
      expect(component.sort.active).toEqual(sortBy);
      expect(component.sort.direction).toEqual(sortOrder);
    });
  });

  describe('parseValuesToParams()', () => {

    it('should update query parameters on sort change', async () => {
      fixture.detectChanges();
      component.sort.sortChange.next({active: sortBy, direction: sortOrder});
      fixture.detectChanges();
      await fixture.whenStable();
      expect(parameterService.setQueryParams).toHaveBeenCalledWith({sortBy, sortOrder});
    });
  });
});
