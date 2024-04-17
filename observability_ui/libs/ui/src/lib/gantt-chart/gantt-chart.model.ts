import { GanttBarDirective } from './gantt-bar.directive';

export interface Position {
  offset: number;
  duration: number;
}

export interface GanttTaskGroup {
  id: string;
  label: string;
  tasks: GanttBarDirective[];
  children: GanttTaskGroup[];
  start_type: 'DEFAULT' | 'SCHEDULED' | 'BATCH' | 'PAYLOAD',
  payload_key?: string;
}
