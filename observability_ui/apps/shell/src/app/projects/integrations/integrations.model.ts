import { InjectionToken } from '@angular/core';
import { AbstractTool } from './tools/abstract-tool.directive';

export type ToolIcon = {_name: string; _displayName: string; _icon: string};

export const INTEGRATION_TOOLS = new InjectionToken<typeof AbstractTool[]>('INTEGRATION_TOOLS', {
  providedIn: 'root',
  factory: () => []
});

export const EXTRA_TOOL_ICONS = new InjectionToken<ToolIcon[]>('EXTRA_TOOL_ICONS', {
  providedIn: 'root',
  factory: () => []
});
