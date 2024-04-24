import { Pipe, PipeTransform } from '@angular/core';
import { parseDate } from '@observability-ui/core';

@Pipe({
  name: 'parseDate',
  standalone: true,
})

export class ParseDatePipe implements PipeTransform {
  transform(value: string) {
    return parseDate(value);
  }
}
