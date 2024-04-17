import { WeekDay } from '@angular/common';

export enum ScheduleSelectorMode {
  EveryHour = 'EveryHour',
  EveryDay = 'EveryDay',
  CertainDays = 'CertainDays',
  Custom = 'Custom',
}

export interface TimeZone {
  label: string;
  tzCode: string;
}

export interface CronParams {
  hour: string;
  minute: string;
  day?: string;
  weekdays?: { [day in WeekDay]: boolean };
  expression?: string;
}

export interface ScheduleInput {
  schedule: string;
  timezone?: string;
}

export const Minutes: string[] = Array.from(Array(60).keys()).map(n => String(n).padStart(2, '0'));
export const Hours: string[] = Array.from(Array(23).keys()).map(n => String(n + 1));
export const Days: string[] = Array.from(Array(31).keys()).map(n => String(n + 1));

export const simplePartPattern: RegExp = /^(\d{1,2})$/;
export const intervalPartPattern: RegExp = /^((\*\/\d{1,2})|\*)$/;
