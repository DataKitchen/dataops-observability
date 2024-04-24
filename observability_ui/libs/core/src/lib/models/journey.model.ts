import { Entity } from "../entity/entity.model";
import { BaseComponent } from "./component.model";

export interface Journey extends Entity {
  project: string;
  instance_rules?: JourneyInstanceRule[];
}

export interface JourneyDag {
  nodes: JourneyDagNode[];
}

export interface JourneyDagNode {
  component: BaseComponent;
  edges: JourneyComponentRelationship[];
}

export interface JourneyDagEdge {  // NOTE: Local type
  id: string;
  from?: string;
  to: string;
}

export interface JourneyComponentRelationship {
  id: string;
  component?: string;
}

export interface JourneyInstanceRule {
  id?: string;
  action: 'START' | 'END' | 'END_PAYLOAD';
  batch_pipeline?: string;
  schedule?: { schedule: string, timezone?: string };
}
