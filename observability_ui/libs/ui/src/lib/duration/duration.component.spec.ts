import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DurationComponent } from './duration.component';
import { MockPipe } from 'ng-mocks';
import { DurationPipe } from './duration.pipe';

describe('run-duration', () => {
  let component: DurationComponent;
  let fixture: ComponentFixture<DurationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        DurationComponent,
        MockPipe(DurationPipe),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DurationComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should be defensive', () => {
    // neither start or end are passed
    // component shouldn't break showing just an empty line
    expect(fixture.debugElement.nativeElement.textContent).toEqual('');
  });
});
