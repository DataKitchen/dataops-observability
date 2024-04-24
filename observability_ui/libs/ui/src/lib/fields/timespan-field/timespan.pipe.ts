import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'timespan'
})

export class TimespanPipe implements PipeTransform {
  transform(value: number): string {
    if (Number.isInteger(value / 86400)) {
      return `${value / 86400} days`;
    } else if (Number.isInteger(value / 3600)) {
      return `${value / 3600} hours`;
    }

    return `${value / 60} minutes`;
  }
}
