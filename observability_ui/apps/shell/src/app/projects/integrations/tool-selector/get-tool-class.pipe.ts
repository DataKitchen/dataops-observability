import { inject, Pipe, PipeTransform } from '@angular/core';
import { EXTRA_TOOL_ICONS, INTEGRATION_TOOLS, ToolIcon } from '../integrations.model';
import { AbstractTool } from '../tools/abstract-tool.directive';

@Pipe({
  name: 'getToolClass',
  standalone: true,
})
export class GetToolClassPipe implements PipeTransform {

  integrations = inject(INTEGRATION_TOOLS);
  extraTools = inject(EXTRA_TOOL_ICONS);

  toolsMap: { [name: string]: typeof AbstractTool | ToolIcon; } = [ ...this.integrations, ...this.extraTools ].reduce<{[name: string]: typeof AbstractTool | ToolIcon}>((map, tool) => {
    map[tool._name.toUpperCase()] = tool;
    return map;
  }, {});

  transform(toolName: string): typeof AbstractTool | ToolIcon {
    return this.toolsMap[toolName?.toUpperCase()];
  }
}
