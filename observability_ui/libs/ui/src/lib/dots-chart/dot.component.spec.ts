import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DotComponent } from './dot.component';

describe('DotComponent', () => {
  let fixture: ComponentFixture<DotComponent>;
  let component: DotComponent;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      imports: [
        DotComponent,
      ],
    });

    fixture = TestBed.createComponent(DotComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });
});
