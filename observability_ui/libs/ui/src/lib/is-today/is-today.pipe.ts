import { Pipe, PipeTransform } from '@angular/core';
import { formatDate } from '@angular/common';

@Pipe({
  name: 'isToday',
  standalone: true
})
export class IsTodayPipe implements PipeTransform {
  transform(value: any): any {
    const today = formatDate(new Date(), 'yyyy.MM.dd', 'en');
    const date = formatDate(value, 'yyyy.MM.dd', 'en');

    return today === date;
  }
}
