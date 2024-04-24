import { ComponentFixture, TestBed } from '@angular/core/testing';
import { Component, ViewChild } from '@angular/core';
import { DagNodeDirective } from './dag-node.directive';

describe('DAG Node Directive', () => {
  let fixture: ComponentFixture<DagNodeTestComponent>;
  let component: DagNodeTestComponent;

  @Component({
    template: `
    <div *dagNode="'myNode'"
      class="node">
      Node Contents
    </div>
    `,
  })
  class DagNodeTestComponent {
    @ViewChild(DagNodeDirective) node: DagNodeDirective;
  }

  beforeEach(async () => {
    TestBed.configureTestingModule({
      declarations: [ DagNodeDirective, DagNodeTestComponent ],
    });

    fixture = TestBed.createComponent(DagNodeTestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should have a center x setter', () => {
    component.node.dagNodeCenterX = 1;
    expect(component.node.centerX).toBe(1);
  });

  it('should have a center y setter', () => {
    component.node.dagNodeCenterY = 1;
    expect(component.node.centerY).toBe(1);
  });

  it('should accept passing a css class for the node wrapper', () => {
    component.node.dagNodeWrapperClass = 'css-class';
    expect(component.node.wrapperClass).toEqual('css-class');
  });

  describe('position getters', () => {
    const x = 15;
    const y = 25;
    const width = 100;
    const height = 60;

    beforeEach(() => {
      component.node.x = x;
      component.node.y = y;
      component.node.width = width;
      component.node.height = height;
    });

    it('should have a left anchor point', () => {
      expect(component.node.left).toEqual({ x, y: y + height / 2 });
    });

    it('should have a top anchor point', () => {
      expect(component.node.top).toEqual({ x: x + width / 2, y: y });
    });

    it('should have a right anchor point', () => {
      expect(component.node.right).toEqual({ x: x + width, y: y + height / 2 });
    });

    it('should have a bottom anchor point', () => {
      expect(component.node.bottom).toEqual({ x: x + width / 2, y: y + height });
    });
  });

  describe('addIncomingEdge()', () => {
    it('should push the edge to the incoming edges array', () => {
      const edgeId = 'edge-1';
      component.node.addIncomingEdge({ id: edgeId } as any);
      expect(component.node.incoming.length).toBe(1);
      expect(component.node.incoming[0]).toEqual({ id: edgeId });
    });
  });

  describe('addOutgoingEdge()', () => {
    it('should push the edge to the outgoing edges array', () => {
      const edgeId = 'edge-1';
      component.node.addOutgoingEdge({ id: edgeId } as any);
      expect(component.node.outgoing.length).toBe(1);
      expect(component.node.outgoing[0]).toEqual({ id: edgeId });
    });
  });

  describe('clearEdges()', () => {
    it('should clear the arrays of incoming and outgoing edges', () => {
      component.node.incoming.push({} as any);
      component.node.outgoing.push({} as any);
      component.node.clearEdges();
      expect(component.node.incoming.length).toBe(0);
      expect(component.node.outgoing.length).toBe(0);
    });
  });
});
