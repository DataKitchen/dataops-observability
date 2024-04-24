import { AfterContentInit, ChangeDetectionStrategy, Component, ContentChild, ContentChildren, DestroyRef, Input, QueryList, WritableSignal, inject, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { CommonModule } from '@angular/common';
import { DotTemplateDirective } from './dot-template.directive';
import { MatIconModule } from '@angular/material/icon';
import { startWith } from 'rxjs';
import { DrillInTemplateDirective } from './drill-in.directive';
import { DkTooltipModule } from '../dk-tooltip';
import { TruncateModule } from '../truncate';
import { difference } from '@observability-ui/core';

interface DotsGroup {
  id: string;
  label: string;
  link: string;
  levelIdx: number;
  expanded: boolean;
  templates: DotTemplateDirective[];
  children: DotsGroup[];
  start_type: string;
  payload_key?: string;
}

type Field = string | ((group: any) => string);

export interface DotsChartLevel {
  groupByField: Field;
  labelField: Field;
  linkField?: Field;
  external?: boolean;
}

@Component({
  selector: 'dots-chart',
  templateUrl: 'dots-chart.component.html',
  styleUrls: [ 'dots-chart.component.scss' ],
  imports: [
    CommonModule,
    MatIconModule,
    DkTooltipModule,
    TruncateModule,
  ],
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DotsChartComponent implements AfterContentInit {
  @Input() levels!: DotsChartLevel[];

  @ContentChild(DrillInTemplateDirective) drillInTemplate!: DrillInTemplateDirective;
  @ContentChildren(DotTemplateDirective) private projectedDots!: QueryList<DotTemplateDirective>;

  groups: WritableSignal<Map<string, DotsGroup>> = signal(new Map<string, DotsGroup>());
  expandedExternalGroup: WritableSignal<DotsGroup | undefined> = signal(undefined);

  private destroyRef = inject(DestroyRef);

  ngAfterContentInit(): void {
    if (this.levels?.length > 0 && !this.levels[0].external) {
      this.projectedDots.changes.pipe(
        startWith(this.projectedDots),
        takeUntilDestroyed(this.destroyRef),
      ).subscribe((dots: QueryList<DotTemplateDirective>) => {
        const dotTemplates = dots.toArray();

        if (!this.levels) {
          return;
        }

        const groups = this.groupDots(dotTemplates, this.levels[0], 0);
        const removedGroups = difference(new Set(this.groups().keys()), new Set(groups.map(g => g.id)));
        this.groups.mutate((currentGroups) => {
          for (const groupId of removedGroups) {
            currentGroups.delete(groupId);
          }

          for (const group of groups) {
            currentGroups.set(group.id, group);
          }
        });

        this.expandedExternalGroup.update((expandedGroup) => {
          if (expandedGroup) {
            const newestGroup = this.groups().get(expandedGroup.id);
            if (newestGroup) {
              const nextLevelIdx = newestGroup!.levelIdx + 1;
              const nextLevel = this.levels[nextLevelIdx];
              const children = this.groupDots(newestGroup!.templates, nextLevel, nextLevelIdx);

              return { ...newestGroup, children };
            }
            return expandedGroup;
          }

          return undefined;
        });
      });
    } else {
      console.error('Unable to render the chart due misconfigured levels');
    }
  }

  toggleExpand(expandingGroup: DotsGroup): void {
    const { id, expanded, levelIdx } = expandingGroup;

    return this.groups.mutate((groups) => {
      const nextLevelIdx = levelIdx + 1;

      if (nextLevelIdx >= this.levels.length) {
        return console.warn('Trying to expand to unsupported level');
      }

      const nextLevel = this.levels[nextLevelIdx];
      const { external } = nextLevel;
      const children = this.groupDots(expandingGroup.templates, nextLevel, nextLevelIdx);

      if (external) {
        return this.expandedExternalGroup.set({ ...expandingGroup, children });
      }

      const group = groups.get(id) as DotsGroup;

      if (expanded) {
        group.expanded = false;
        return;
      }

      group.children = children;
      group.expanded = true;
    });
  }

  closeExternalExpandedGroup(): void {
    this.expandedExternalGroup.set(undefined);
  }

  private groupDots(dots: DotTemplateDirective[], level: DotsChartLevel, levelIdx: number): DotsGroup[] {
    const { groupByField, labelField, linkField } = level;

    return Array.from(dots.reduce((groups, dot) => {
      const groupBy = this.getFieldValue(dot, groupByField);
      if (!groups.has(groupBy)) {
        groups.set(groupBy, {
          id: groupBy,
          label: this.getFieldValue(dot, labelField),
          link: this.getFieldValue(dot, linkField),
          levelIdx,
          templates: [],
          expanded: false,
          children: [],
          start_type: this.getPropValue(dot, 'start_type'),
          payload_key: this.getPropValue(dot, 'payload_key')
        });
      }

      groups.get(groupBy)?.templates.push(dot);

      return groups;
    }, new Map<string, DotsGroup>()).values());
  }

  private getFieldValue(dot: DotTemplateDirective, field: Field | undefined): string {
    let value = '';
    if (typeof field === 'string') {
      value = this.getPropValue(dot, field);
    } else if (typeof field === 'function') {
      value = field(dot.value);
    }

    return value;
  }

  private getPropValue(dot: DotTemplateDirective, key: string): any | undefined {
    return key.split('.').reduce((current, nextKey) => {
      return current?.[nextKey];
    }, dot.value as any);
  }
}
