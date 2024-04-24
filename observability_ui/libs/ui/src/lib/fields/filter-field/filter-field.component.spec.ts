import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, ViewChild } from '@angular/core';
import { FilterFieldOptionComponent } from './filter-field-option.component';
import { FilterFieldModule } from './filter-field.module';
import { FilterFieldComponent } from './filter-field.component';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { rxjsScheduler } from '@datakitchen/ngx-toolkit';

describe('filter-field', () => {

  @Component({
    selector: 'test-component',
    template: `
      <!--  Basic filter single select without form -->
      <filter-field #filterFieldComponent
        label="basic filter"
        (change)="filterChange($event)"
        [multiple]="multiselect">
        <ng-container *ngFor="let option of [1,2,3,4,5,6,7]">
          <filter-field-option [value]="option">{{option}}</filter-field-option>
        </ng-container>
      </filter-field>

      <filter-field #filterFieldComponentWithControl
        [formControl]="control"
        [searchable]="true"
        [multiple]="multiselect">
        <ng-container *ngFor="let option of options">
          <filter-field-option [value]="option">{{option}}</filter-field-option>
        </ng-container>
      </filter-field>
    `
  })
  class TestComponent {
    options = [ 'alice', 'bob', 'carl', 'denise', 'eleonore', 'fabius' ];

    control = new FormControl();

    @ViewChild('filterFieldComponent')
    filterFieldComponent: FilterFieldComponent;

    @ViewChild('filterFieldComponentWithControl')
    filterFieldComponentWithFormControl: FilterFieldComponent;

    multiselect = false;

    outputSpy: jest.Mock = jest.fn();

    filterChange(options: FilterFieldOptionComponent[]) {
      this.outputSpy(options);
    }
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;
  let testScheduler: TestScheduler;

  beforeEach(async () => {
    testScheduler = new TestScheduler();

    await TestBed.configureTestingModule({
      imports: [
        FilterFieldModule,
        ReactiveFormsModule,
        CommonModule
      ],
      declarations: [ TestComponent ],
      providers: [
        {
          provide: rxjsScheduler,
          useValue: testScheduler,
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.autoDetectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('items selection', () => {

    describe('multi select is off', () => {

      it('select an item', () => {

        // select an item
        component.filterFieldComponent.select({ checked: true }, component.filterFieldComponent.options.first);
        expect(component.outputSpy).toHaveBeenCalledWith([ expect.objectContaining({ label: '1', selected: true }) ]);

        // select another item. only latest selected item should be passed
        component.filterFieldComponent.select({ checked: true }, component.filterFieldComponent.options.last);
        expect(component.outputSpy).toHaveBeenCalledWith([ expect.objectContaining({ label: '7', selected: true }) ]);

        // unselect selected item
        component.filterFieldComponent.select({ checked: false }, component.filterFieldComponent.options.last);
        expect(component.outputSpy).toHaveBeenCalledWith([]);
      });

    });


    describe('multi select is on', () => {

      beforeEach(() => {
        component.multiselect = true;
        fixture.detectChanges();
      });

      it('select some items', () => {

        // select an item
        component.filterFieldComponent.select({ checked: true }, component.filterFieldComponent.options.first);
        expect(component.outputSpy).toHaveBeenCalledWith([ expect.objectContaining({ label: '1', selected: true }) ]);

        // add another item to selection
        component.filterFieldComponent.select({ checked: true }, component.filterFieldComponent.options.last);
        expect(component.outputSpy).toHaveBeenCalledWith(
          [
            expect.objectContaining({ label: '1', selected: true }),
            expect.objectContaining({ label: '7', selected: true })
          ]
        );

        // unselect one the selected items
        component.filterFieldComponent.select({ checked: false }, component.filterFieldComponent.options.first);
        expect(component.outputSpy).toHaveBeenCalledWith([ expect.objectContaining({ label: '7', selected: true }) ]);

      });

      it('should select/unselect all', () => {
        component.filterFieldComponent.selectAllChange({ checked: true });

        expect(component.outputSpy).toHaveBeenCalledWith([
          expect.objectContaining({ label: '1', selected: true }),
          expect.objectContaining({ label: '2', selected: true }),
          expect.objectContaining({ label: '3', selected: true }),
          expect.objectContaining({ label: '4', selected: true }),
          expect.objectContaining({ label: '5', selected: true }),
          expect.objectContaining({ label: '6', selected: true }),
          expect.objectContaining({ label: '7', selected: true }),
        ]);

        component.filterFieldComponent.selectAllChange({ checked: false });
        expect(component.outputSpy).toHaveBeenCalledWith([]);

      });

    });
  });

  describe('used with a form control', () => {

    it('should select values provided from from control', () => {
      component.control.patchValue('alice,bob,carl');

      expect(component.filterFieldComponentWithFormControl.selected).toEqual([
        expect.objectContaining({ label: 'alice' }),
        expect.objectContaining({ label: 'bob' }),
        expect.objectContaining({ label: 'carl' }),
      ]);
    });

    it('should filter the options when searching', async () => {

      await fixture.whenStable();

      const options = component.filterFieldComponentWithFormControl.options
        .filter(o => o.label.includes('fabius'));

      testScheduler.run(({ expectObservable }) => {

        component.filterFieldComponentWithFormControl.searchControl.setValue('fabius');
        // component.filterFieldComponentWithFormControl.searchControl.reset();

        expectObservable(component.filterFieldComponentWithFormControl.filteredOptions$).toBe('a 299ms b', {
          a: expect.anything(),
          b: options
        });
      });
    });

    it('should show all options when clearing search', async () => {

      await fixture.whenStable();

      const options = component.filterFieldComponentWithFormControl.options
        .toArray();
      testScheduler.run(({ expectObservable }) => {

        component.filterFieldComponentWithFormControl.searchControl.setValue('fabius');
        component.filterFieldComponentWithFormControl.searchControl.reset();

        expectObservable(component.filterFieldComponentWithFormControl.filteredOptions$).toBe('a 299ms b', {
          a: expect.anything(),
          b: options
        });
      });
    });
  });

});
