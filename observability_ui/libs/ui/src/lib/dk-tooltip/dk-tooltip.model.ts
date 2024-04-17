import { ConnectedPosition } from '@angular/cdk/overlay';

const oppositePositions: { [placement in Placement]: Placement } = {
  top: 'bottom',
  bottom: 'top',
  left: 'right',
  right: 'left',
};

export type Placement = 'top' | 'bottom' | 'left' | 'right';

export const POSITIONS: { [placement in Placement]: ConnectedPosition } = {
  top: {originX: 'center', originY: 'top', overlayX: 'center', overlayY: 'bottom'},
  bottom: {originX: 'center', originY: 'bottom', overlayX: 'center', overlayY: 'top'},
  left: {originX: 'start', originY: 'center', overlayX: 'end', overlayY: 'center'},
  right: {originX: 'end', originY: 'center', overlayX: 'start', overlayY: 'center'},
};

export function getOppositePosition(placement: Placement): ConnectedPosition {
  const opposite = oppositePositions[placement];
  return POSITIONS[opposite];
}
