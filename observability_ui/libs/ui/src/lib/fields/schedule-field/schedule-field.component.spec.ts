import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockComponent, MockModule } from 'ng-mocks';
import { MatCheckbox } from '@angular/material/checkbox';
import { ScheduleFieldComponent } from './schedule-field.component';
import { OverlayModule } from '@angular/cdk/overlay';
import { MatIcon } from '@angular/material/icon';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { Component, ViewChild } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { ScheduleSelectorMode } from './schedule-field.model';
import { Schedule } from '@observability-ui/core';

describe('schedule-field', () => {
  @Component({
    selector: 'test-component',
    template: `
      <schedule-field label="my label" hint="my hint" [formControl]="form" #field></schedule-field>
    `
  })
  class TestComponent {
    @ViewChild('field') scheduleField: ScheduleFieldComponent;

    form = new FormControl();
  }

  let testComponent: TestComponent;
  let testComponentFixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        TestComponent,
        ScheduleFieldComponent,
        MockComponent(MatIcon),
        MockComponent(MatCheckbox),
      ],
      imports: [
        MockModule(OverlayModule),
        MockModule(MatInputModule),
        ReactiveFormsModule,
      ],
    }).compileComponents();

    testComponentFixture = TestBed.createComponent(TestComponent);
    testComponent = testComponentFixture.componentInstance;
  });

  it('should create', () => {
    expect(testComponent).toBeTruthy();
  });

  describe('openEditor()', () => {
    const $event = { stopImmediatePropagation: jest.fn() } as any;

    beforeEach(async () => {
      testComponentFixture.detectChanges();
      await testComponentFixture.whenRenderingDone();
    });

    it('should stop the event propagation', () => {
      const mock = jest.fn();
      testComponent.scheduleField.openEditor({ stopImmediatePropagation: mock } as any);
      expect(mock).toBeCalled();
    });

    it('should open the editor', () => {
      testComponent.scheduleField.openEditor($event);
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(testComponent.scheduleField.editorOpened$).toBe('a', { a: true });
      });
    });

    describe('when detecting the mode', () => {
      it('should select `EveryHour` mode if no value', () => {
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryHour);
      });

      it('should select `Custom` mode if month of year is set', () => {
        testComponent.form.setValue({ schedule: '0 * * 1 *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.Custom);
      });

      it('should select `EveryHour` mode if hours interval and minutes are set', () => {
        testComponent.form.setValue({ schedule: '10 */3 * * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryHour);
      });

      it('should select `EveryHour` mode if hours is set to * and minutes are set', () => {
        testComponent.form.setValue({ schedule: '25 * * * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryHour);
      });

      it('should select `Custom` mode if hours has some special value', () => {
        testComponent.form.setValue({ schedule: '5 */2,3 * * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.Custom);
      });

      it('should select `EveryDay` mode if day interval, hours and minutes are set', () => {
        testComponent.form.setValue({ schedule: '10 3 */5 * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryDay);
      });

      it('should select `EveryDay` mode if day is set to *, and hours and minutes are set', () => {
        testComponent.form.setValue({ schedule: '10 3 * * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryDay);
      });

      it('should select `Custom` mode if days has some special value', () => {
        testComponent.form.setValue({ schedule: '10 3 */5,3 * *', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.Custom);
      });

      it('should select `Custom` mode if days interval is set but weekdays is also set', () => {
        testComponent.form.setValue({ schedule: '10 3 */5,3 * SAT', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.Custom);
      });

      it('should select `CertainDays` mode if weekdays, hours and minutes are set', () => {
        testComponent.form.setValue({ schedule: '10 3 * * MON-WED', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.CertainDays);
      });

      it('should select `Custom` mode if weekdays is set, but days is also set', () => {
        testComponent.form.setValue({ schedule: '10 3 */2 * MON-WED', timezone: 'UTC' } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.Custom);
      });
    });

    describe('when initializing the form', () => {
      it('should use the default expression if value is not set', () => {
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({ minute: '00', hour: '1' }));
      });

      it('should set the timezone to default if not set', () => {
        testComponent.form.setValue({ schedule: '0 * * * *', timezone: null as any } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({ timezone: testComponent.scheduleField['userTimezone'] }));
      });

      it('should set the hour and minute for `EveryHour` mode', () => {
        testComponent.form.setValue({ schedule: '0 */3 * * *', timezone: null as any } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({ hour: '3', minute: '00' }));
      });

      it('should set the day, hour and minute for `EveryDay` mode', () => {
        testComponent.form.setValue({ schedule: '10 3 */2 * *', timezone: null as any } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({ day: '2', hour: '3', minute: '10' }));
      });

      it('should set weekdays, hour and minute for `CertainDays` mode', () => {
        testComponent.form.setValue({ schedule: '10 3 * * MON-WED', timezone: null as any } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({
          hour: '3',
          minute: '10',
          weekdays: { 0: false, 1: true, 2: true, 3: true, 4: false, 5: false, 6: false },
        }));
      });

      it('should set the expression for `Custom` mode', () => {
        testComponent.form.setValue({ schedule: '10 */2 */2 1 *', timezone: null as any } as Schedule, {emitEvent: false});
        testComponent.scheduleField.openEditor($event);
        expect(testComponent.scheduleField.form.value).toEqual(expect.objectContaining({ expression: '10 */2 */2 1 *' }));
      });
    });
  });

  describe('closeEditor()', () => {
    beforeEach(async () => {
      testComponentFixture.detectChanges();
      await testComponentFixture.whenRenderingDone();
    });

    it('should close the editor', () => {
      testComponent.scheduleField.openEditor({ stopImmediatePropagation: jest.fn() } as any);
      testComponent.scheduleField.closeEditor();
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(testComponent.scheduleField.editorOpened$).toBe('a', { a: false});
      });
    });
  });

  describe('selectMode()', () => {
    beforeEach(async () => {
      testComponentFixture.detectChanges();
      await testComponentFixture.whenRenderingDone();
    });

    it('should set the selected mode', () => {
      testComponent.scheduleField.selectMode(ScheduleSelectorMode.EveryDay);
      expect(testComponent.scheduleField.selectedMode$.getValue()).toEqual(ScheduleSelectorMode.EveryDay);
    });
  });

  describe('apply()', () => {
    beforeEach(async () => {
      testComponentFixture.detectChanges();
      await testComponentFixture.whenRenderingDone();
    });

    it('should set the value of the control with the expression and timezone', () => {
      const expectedExpression = '10 3 */2 * *';
      const expectedTimezone = 'America/New_York';

      testComponent.scheduleField.selectMode(ScheduleSelectorMode.EveryDay);
      testComponent.scheduleField.form.patchValue({
        day: '2',
        hour: '3',
        minute: '10',
        timezone: expectedTimezone,
      });
      testComponent.scheduleField.apply();
      expect(testComponent.form.value).toEqual({ schedule: expectedExpression, timezone: expectedTimezone });
    });

    it('should mark the the control dirty', () => {
      testComponent.scheduleField.selectMode(ScheduleSelectorMode.EveryDay);
      testComponent.scheduleField.form.patchValue({
        day: '2',
        hour: '3',
        minute: '10',
        timezone: 'America/New_York',
      });
      testComponent.scheduleField.apply();
      expect(testComponent.form.dirty).toBeTruthy();
    });

    it('should close the editor', () => {
      testComponent.scheduleField.openEditor({ stopImmediatePropagation: jest.fn() } as any);
      testComponent.scheduleField.apply();
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(testComponent.scheduleField.editorOpened$).toBe('a', {a: false});
      });
    });
  });

  describe('clear()', () => {
    beforeEach(async () => {
      testComponentFixture.detectChanges();
      await testComponentFixture.whenRenderingDone();
    });

    it('should set the control value to null', () => {
      testComponent.scheduleField.clear();
      expect(testComponent.form.value).toEqual({
        schedule: undefined,
        timezone: undefined,
      });
    });

    it('should close the editor', () => {
      testComponent.scheduleField.openEditor({ stopImmediatePropagation: jest.fn() } as any);
      testComponent.scheduleField.apply();
      new TestScheduler().run(({ expectObservable }) => {
        expectObservable(testComponent.scheduleField.editorOpened$).toBe('a', {a: false});
      });
    });
  });
});
