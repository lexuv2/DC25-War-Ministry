import { waitForAsync, ComponentFixture, TestBed } from '@angular/core/testing';

import { CvTableComponent } from './cv-table.component';

describe('CvTableComponent', () => {
  let component: CvTableComponent;
  let fixture: ComponentFixture<CvTableComponent>;

  beforeEach(() => {
    fixture = TestBed.createComponent(CvTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should compile', () => {
    expect(component).toBeTruthy();
  });
});
