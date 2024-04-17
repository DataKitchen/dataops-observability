import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyMenuModule as MatMenuModule } from '@angular/material/legacy-menu';
import { MatIconModule } from '@angular/material/icon';
import { Component } from '@angular/core';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { LabeledMenuModule } from './labeled-menu.module';

describe('labeled-menu', () => {

  @Component({
    selector: 'test-labeled-menu',
    template: `
      <labeled-menu [label]="menuControl.value">
        <button mat-button (click)="menuControl.setValue('Open')">Open</button>
        <button mat-button (click)="menuControl.setValue('Close')">Close</button>
        <button mat-button (click)="menuControl.setValue('Quit')">Quit</button>
      </labeled-menu>
    `,
  })
  class TestingComponent {
    selected!: string;

    menuControl = new FormControl('Default');
  }

  let fixture: ComponentFixture<TestingComponent>;

  beforeEach(async () => {

    await TestBed.configureTestingModule({
      imports: [
        MatMenuModule,
        MatIconModule,
        LabeledMenuModule,
        ReactiveFormsModule,
      ],
      declarations: [
        TestingComponent,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestingComponent);

    fixture.autoDetectChanges();
  });

  it('should create', () => {
    expect(fixture.componentInstance).toBeTruthy();
  });

});
