import { AfterContentInit, AfterViewInit, OnDestroy, OnInit } from '@angular/core';
import { $Keys, Optional } from 'utility-types';
import 'reflect-metadata';

interface ComponentClass extends Optional<OnInit>, Optional<AfterViewInit>, Optional<AfterContentInit>, Optional<OnDestroy> {
  [K: string]: any
}

const noop = () => { void 1; };

const HOST_RESIZE_METADATA = Symbol('HOST_RESIZE_METADATA');

export function OnHostResized(elementName: string = 'element', hook: $Keys<ComponentClass> = 'ngOnInit') {
  return function (target: ComponentClass, methodName: string | symbol, descriptor: TypedPropertyDescriptor<any>): TypedPropertyDescriptor<any> {

    const originalHook = target[hook] || noop;
    const ngOnDestroy = target.ngOnDestroy || noop;

    target[hook] = function (): void {
      originalHook.call(this);

      if (!this[elementName]) {
        console.warn('Attempt to use OnHostResized failed - Inject the component\'s ElementRef');
      }

      const observer: ResizeObserver = new ResizeObserver(() => {
        descriptor.value.call(this);
      });

      observer.observe(this[elementName]?.nativeElement);

      Reflect.defineMetadata(HOST_RESIZE_METADATA, observer, this);
    };

    target.ngOnDestroy = function () {
      ngOnDestroy.call(this);

      const observer = Reflect.getMetadata(HOST_RESIZE_METADATA, this);

      observer?.disconnect();
    };

    return descriptor;
  };
}
