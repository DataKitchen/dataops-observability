import { TemplateRef } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { MockProvider } from 'ng-mocks';
import { GanttBarDirective } from './gantt-bar.directive';

describe('GanttBarDirective', () => {
  let directive: GanttBarDirective;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      providers: [
        GanttBarDirective,
        MockProvider(TemplateRef),
      ],
    });

    directive = TestBed.inject(GanttBarDirective);
  });

  it('should create', () => {
    expect(directive).toBeDefined();
  });

  it('should update the signal when setting the start time', () => {
    const date = new Date();
    directive.ganttBarStart = date;
    expect(directive.start()).toEqual(date);
  });

  it('should update the signal when setting the end time', () => {
    const date = new Date();
    directive.ganttBarEnd = date;
    expect(directive.end()).toEqual(date);
  });
});
