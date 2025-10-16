import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HrHomeComponent } from './hr-home.component';

describe('HrHomeComponent', () => {
  let component: HrHomeComponent;
  let fixture: ComponentFixture<HrHomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HrHomeComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HrHomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
