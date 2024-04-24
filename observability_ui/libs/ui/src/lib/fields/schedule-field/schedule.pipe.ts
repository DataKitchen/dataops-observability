import { Pipe, PipeTransform } from '@angular/core';
import cronstrue from 'cronstrue';
import { Schedule } from '@observability-ui/core';

@Pipe({
  name: 'schedule',
})
export class SchedulePipe implements PipeTransform {
  public transform(schedule?: Schedule | null): string {
    if (!schedule?.schedule) {
      return '...';
    }

    return `${cronstrue.toString(schedule.schedule).replace('At ', '').toLowerCase()}${schedule.timezone ? ' (' + schedule.timezone + ')' : ''}`;
  }
}
