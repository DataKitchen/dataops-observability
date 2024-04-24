import { TestBed, ComponentFixture } from '@angular/core/testing';
import { BreadcrumbComponent } from './breadcrumb.component';

describe('Breadcrumb Component', () => {
  let fixture: ComponentFixture<BreadcrumbComponent>;
  let component: BreadcrumbComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [],
      declarations: [],
      providers: [],
    });

    fixture = TestBed.createComponent(BreadcrumbComponent);
    component = fixture.componentInstance;
  });

  it('should exist', () => {
    expect(component).toBeDefined();
  });
});
