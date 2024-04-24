import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'duration',
})
export class DurationPipe implements PipeTransform {
  public transform(startDate: string | Date, endDate: string | Date, cap: number = 1000/*days*/ * 24 * 60 * 60 * 1000): string {
    if (!startDate || !endDate) {
      return '';
    }

    const milliseconds = Math.abs(new Date(endDate).valueOf() - new Date(startDate).valueOf());
    if (milliseconds > cap) {
      return '1000d+';
    }
    return this.format(milliseconds);
  }

  private format(milliseconds: number, units: number = 2): string {
    return [ this.days(milliseconds), this.hours(milliseconds), this.minutes(milliseconds), this.seconds(milliseconds) ].filter((v) => v).slice(0, units).join(' ') || '0s';
  }

  private days(milliseconds: number): string | null {
    const value = Math.trunc(milliseconds / 1000 / 60 / 60 / 24);
    if (value <= 0) {
      return null;
    }
    return `${value}d`;
  }

  private hours(milliseconds: number): string | null {
    const value = Math.trunc((milliseconds / 1000 / 60 / 60) % 24);
    if (value <= 0) {
      return null;
    }
    return `${value}h`;
  }

  private minutes(milliseconds: number): string | null {
    const value = Math.trunc((milliseconds / 1000 / 60) % 60);
    if (value <= 0) {
      return null;
    }
    return `${value}m`;
  }

  private seconds(milliseconds: number): string | null {
    const value = Math.trunc((milliseconds / 1000) % 60);
    if (value <= 0) {
      return null;
    }
    return `${value}s`;
  }
}
