import { Entity } from '../entity';

export enum ComponentType {
  BatchPipeline = "BATCH_PIPELINE",
  StreamingPipeline = "STREAMING_PIPELINE",
  Dataset = "DATASET",
  Server = "SERVER",
}

export interface BaseComponent extends Entity {
  name: string;
  key: string;
  type: ComponentType;
  display_name?: string;
  labels?: object; // NOTE: We need to figure out how this looks like
  tool?: string;
  // setting this to optional so that when using this type within `TypedForms`
  // we won't need to add this field. We'll get it from the router params
  readonly project_id?: string;
}

export interface Schedule {
  readonly id: string;
  readonly component_id?: string;

  schedule: string;
  timezone?: string;
  margin: number;
  expectation?: 'BATCH_PIPELINE_START_TIME' | 'BATCH_PIPELINE_END_TIME' | 'DATASET_ARRIVAL';
}

export interface ChangedScheduleExpectation extends Schedule {
  changed: boolean;
  deleted: boolean;
}
export interface ShortComponent {
  id: string;
  display_name: string;
  type: ComponentType;
  tool?: string;
}
