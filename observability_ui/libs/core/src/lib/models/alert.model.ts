export interface Alert<AlertType> {
  /**
   * Where `Type` must be an enum with possible types such as
   *
   * export enum AlertType {
   *   lateStart = <any>'LATE_START',
   *   lateEnd = <any>'LATE_END',
   * }
   */

  id: string;
  run: string;
  level: AlertLevel;
  type: AlertType;
  name?: string;
  description: string;
  created_on: string;
}

export type AlertLevel = 'WARNING' | 'ERROR';
