import { TemplatePortal } from '@angular/cdk/portal';
import { WeekDay } from '@angular/common';
import { AfterViewInit, Component, Input, OnInit, Optional, Self, TemplateRef, ViewChild, ViewContainerRef } from '@angular/core';
import { AbstractControl, FormControl, FormGroup, NgControl } from '@angular/forms';
import { CronBuilder } from 'cron-builder-ts';
import { parseExpression } from 'cron-parser';
import cronstrue from 'cronstrue';
import { getAllTimezones, getTimezone } from 'countries-and-timezones';
import { BehaviorSubject, filter, map, pairwise, Subject, takeUntil } from 'rxjs';
import { AbstractField } from '../abstract-field';
import { CronParams, Days, Hours, intervalPartPattern, Minutes, ScheduleSelectorMode, simplePartPattern, TimeZone } from './schedule-field.model';
import { Schedule } from '@observability-ui/core';

@Component({
  selector: 'schedule-field',
  templateUrl: './schedule-field.component.html',
  styleUrls: [ './schedule-field.component.scss' ],
})
export class ScheduleFieldComponent extends AbstractField<{
  schedule: string;
  timezone: string;
}> implements OnInit, AfterViewInit {
  @Input() label!: string;
  @Input() placeholder!: string;
  @Input() hint!: string;
  @Input() autofocus: boolean = false;
  @Input() externalLabel: boolean = false;

  portal$: Subject<TemplatePortal | null> = new BehaviorSubject<TemplatePortal | null>(null);
  editorOpened$: Subject<boolean> = new BehaviorSubject<boolean>(false);
  selectedMode$: BehaviorSubject<ScheduleSelectorMode> = new BehaviorSubject<ScheduleSelectorMode>(ScheduleSelectorMode.EveryHour);

  cronExpression$: BehaviorSubject<string> = new BehaviorSubject<string>('');
  nextTime$: BehaviorSubject<Date | null> = new BehaviorSubject<Date | null>(null);

  days: string[] = Days;
  hours: string[] = Hours;
  minutes: string[] = Minutes;


  Timezones: TimeZone[] = [
    { label: 'UTC (GMT+00:00)', tzCode: 'UTC' } as TimeZone,
    ...Object.values(getAllTimezones()).map(t => ({
      label: `${t.name} (GMT${t.utcOffsetStr})`,
      tzCode: t.name
    })).sort((a, b) => a.label.localeCompare(b.label))
  ];
  ScheduleSelectorMode = ScheduleSelectorMode;

  displayControl = new FormControl<string>('');

  form = new FormGroup<{
    day: FormControl<string>;
    hour: FormControl<string>;
    minute: FormControl<string>;
    weekdays: FormGroup<{ [day in WeekDay]: FormControl<boolean | null> }>;
    timezone: FormControl<string | null>;
    expression: FormControl<string>;
  }>({
    day: new FormControl<string>('1') as FormControl<string>,
    hour: new FormControl<string>('1') as FormControl<string>,
    minute: new FormControl<string>('00') as FormControl<string>,
    weekdays: new FormGroup({
      [WeekDay.Sunday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Monday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Tuesday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Wednesday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Thursday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Friday]: new FormControl(null) as FormControl<boolean | null>,
      [WeekDay.Saturday]: new FormControl(null) as FormControl<boolean | null>,
    }),
    timezone: new FormControl<string | null>(null),
    expression: new FormControl<string>('', this.isExpressionValid) as FormControl<string>,
  });

  @ViewChild('everyHour') private everyHourTemplate!: TemplateRef<unknown>;
  @ViewChild('everyDay') private everyDayTemplate!: TemplateRef<unknown>;
  @ViewChild('certainDays') private certainDaysTemplate!: TemplateRef<unknown>;
  @ViewChild('custom') private customTemplate!: TemplateRef<unknown>;

  private modeToTemplateMap!: Map<ScheduleSelectorMode, TemplatePortal>;
  private readonly defaultSchedule: string = '0 * * * *';
  private readonly userTimezone = this.getUserTimezone();

  constructor(
    @Self() @Optional() protected override ngControl: NgControl,
    private viewContainerRef: ViewContainerRef,
  ) {
    super(ngControl);
  }

  override ngOnInit(): void {
    super.ngOnInit();

    this.selectedMode$.pipe(
      pairwise(),
      map<[ ScheduleSelectorMode, ScheduleSelectorMode ], [ ScheduleSelectorMode, TemplatePortal ]>(([ previousMode, currentMode ]) => [ previousMode, this.modeToTemplateMap?.get(currentMode) as TemplatePortal ]),
      filter(([ , template ]) => !!template),
      takeUntil(this.destroyed$),
    ).subscribe(([ previousMode, template ]) => {
      this.portal$.next(template);
      this.form.patchValue({ expression: this.getCronExpression(previousMode, this.form.value as CronParams) });
    });

    this.form.valueChanges.pipe(
      takeUntil(this.destroyed$),
    ).subscribe((value) => {
      const tz = value.timezone ?? 'UTC';
      const expression = this.getCronExpression(this.selectedMode$.getValue(), value as CronParams);

      if (!this.isExpressionValid({ value: expression } as AbstractControl)) {
        this.cronExpression$.next(expression);
        this.nextTime$.next(parseExpression(expression, { tz }).next().toDate());
      } else {
        this.nextTime$.next(null);
        this.cronExpression$.next('');
      }
    });

    this.displayControl.disable();
  }

  override ngAfterViewInit(): void {
    super.ngAfterViewInit();

    this.modeToTemplateMap = new Map([
      [ ScheduleSelectorMode.EveryHour, new TemplatePortal(this.everyHourTemplate, this.viewContainerRef) ],
      [ ScheduleSelectorMode.EveryDay, new TemplatePortal(this.everyDayTemplate, this.viewContainerRef) ],
      [ ScheduleSelectorMode.CertainDays, new TemplatePortal(this.certainDaysTemplate, this.viewContainerRef) ],
      [ ScheduleSelectorMode.Custom, new TemplatePortal(this.customTemplate, this.viewContainerRef) ],
    ]);
  }

  override writeValue(value: Schedule): void {

    const { schedule, timezone } = value || {};

    const values = this.getReadableCronExpression(schedule, timezone);
    this.displayControl.patchValue(values);
  }

  openEditor(event: Event): void {
    event.stopImmediatePropagation();
    this.initializeFromValue(this.control.value);
    this.editorOpened$.next(true);
  }

  closeEditor(): void {
    this.editorOpened$.next(false);
  }

  selectMode(mode: ScheduleSelectorMode): void {
    if (mode === ScheduleSelectorMode.EveryHour && this.form.controls.hour.value === '0') {
      this.form.patchValue({
        hour: '1'
      });
    }

    this.selectedMode$.next(mode);
  }

  apply(): void {
    const timezone = this.form.value.timezone;
    const expression = this.getCronExpression(this.selectedMode$.getValue(), this.form.value as CronParams);

    this.control.patchValue({
      ...this.control.value,
      schedule: expression,
      timezone
    } as Schedule);
    this.control.markAsDirty();
    this.closeEditor();
  }

  clear(): void {
    this.control.patchValue({
      ...this.control.value,
      // preserve other values just reset `schedule` and `timezone`
      schedule: undefined,
      timezone: undefined,
    });
    this.control.markAsDirty();
    this.closeEditor();
  }

  private isExpressionValid(control: AbstractControl): { invalidCron: boolean } | null {
    try {
      parseExpression(control.value);
      cronstrue.toString(control.value);
    } catch {
      return { invalidCron: true };
    }

    return null;
  }

  private getCronExpression(mode: ScheduleSelectorMode, {
    hour,
    minute,
    day,
    weekdays = {} as any,
    expression
  }: CronParams): string {
    const expressionBuilder = new CronBuilder();

    expressionBuilder.addValue('hour', hour);
    expressionBuilder.addValue('minute', Number(minute).toFixed(0));

    if (mode === ScheduleSelectorMode.EveryHour) {
      expressionBuilder.removeValue('hour', hour);
      expressionBuilder.addValue('hour', hour === '1' ? '*' : `*/${hour}`);
    } else if (mode === ScheduleSelectorMode.EveryDay) {
      expressionBuilder.addValue('dayOfTheMonth', day === '1' ? '*' : `*/${day}`);
    } else if (mode === ScheduleSelectorMode.CertainDays) {
      for (const [ wDay, included ] of Object.entries(weekdays)) {
        if (included) {
          expressionBuilder.addValue('dayOfTheWeek', String(wDay));
        }
      }
    } else if (mode === ScheduleSelectorMode.Custom) {
      return expression as string;
    }
    return expressionBuilder.build({ plain: false, outputWeekdayNames: true });
  }

  private initializeFromValue(value?: Schedule): void {
    const mode = this.getModeFromValue(value);
    const expression = value?.schedule ?? this.defaultSchedule;
    const timezone = value?.timezone ?? this.userTimezone ?? 'UTC';
    const parserByMode = {
      [ScheduleSelectorMode.EveryHour]: this.formValueForHourMode.bind(this),
      [ScheduleSelectorMode.EveryDay]: this.formValueForDayMode.bind(this),
      [ScheduleSelectorMode.CertainDays]: this.formValueForCertainDaysMode.bind(this),
      [ScheduleSelectorMode.Custom]: this.formValueForCustomMode.bind(this),
    };
    const parserFn = parserByMode[mode];

    this.selectedMode$.next(mode);
    this.form.patchValue({ timezone, ...parserFn(expression) });
  }

  private getModeFromValue(value?: Schedule): ScheduleSelectorMode {
    if (!value || !value.schedule) {
      return ScheduleSelectorMode.EveryHour;
    }

    const [ minute, hour, day, ] = value.schedule.split(' ');
    const cronExpression = parseExpression(value.schedule, { tz: value.timezone ?? 'UTC' });

    const daysOfMonthSet = cronExpression.fields.dayOfMonth.length !== this.days.length;
    const weekDaysSet = cronExpression.fields.dayOfWeek.length !== 8;
    const monthsSet = cronExpression.fields.month.length !== 12;

    if (!monthsSet) {
      const hourSimple = simplePartPattern.test(hour);
      const minuteSimple = simplePartPattern.test(minute);
      const hourIntervals = intervalPartPattern.test(hour);
      const dayIntervals = intervalPartPattern.test(day);

      if (hourIntervals && minuteSimple && !daysOfMonthSet && !weekDaysSet) {
        return ScheduleSelectorMode.EveryHour;
      } else if (hourSimple && minuteSimple && dayIntervals && !weekDaysSet) {
        return ScheduleSelectorMode.EveryDay;
      } else if (hourSimple && minuteSimple && weekDaysSet && !daysOfMonthSet) {
        return ScheduleSelectorMode.CertainDays;
      }
    }

    return ScheduleSelectorMode.Custom;
  }

  private formValueForHourMode(expression: string): Partial<CronParams> {
    const [ minute, hour, ] = expression.split(' ');
    const [ , hourValue ] = hour.split('/');

    return { minute: minute.padStart(2, '0'), hour: hourValue ?? '1' };
  }

  private formValueForDayMode(expression: string): Partial<CronParams> {
    const [ minute, hour, day, ] = expression.split(' ');
    const [ , dayValue ] = day.split('/');

    return { minute: minute.padStart(2, '0'), hour, day: dayValue ?? '1' };
  }

  private formValueForCertainDaysMode(expression: string): Partial<CronParams> {
    const [ minute, hour, ] = expression.split(' ');
    const parsedExpression = parseExpression(expression);
    const weekdays = parsedExpression.fields.dayOfWeek;

    return {
      hour,
      minute: minute.padStart(2, '0'),
      weekdays: {
        0: weekdays.includes(0),
        1: weekdays.includes(1),
        2: weekdays.includes(2),
        3: weekdays.includes(3),
        4: weekdays.includes(4),
        5: weekdays.includes(5),
        6: weekdays.includes(6),
      },
    };
  }

  private formValueForCustomMode(expression: string): Partial<CronParams> {
    return { expression };
  }

  private getReadableCronExpression(expression: string, timezone: string | undefined): string | null {
    if (!timezone && !expression) {
      return null;
    }

    if (expression) {
      return `${cronstrue.toString(expression)} (${timezone})`;
    }

    return `(${timezone})`;
  }

  private getUserTimezone(): string | undefined | null {
    const timezone = getTimezone(Intl.DateTimeFormat().resolvedOptions().timeZone);

    if (!timezone) {
      return undefined;
    }

    if (timezone.deprecated) {
      return timezone.aliasOf;
    }

    return timezone.name;
  }
}
