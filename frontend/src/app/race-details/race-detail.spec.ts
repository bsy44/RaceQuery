import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RaceDetail } from './race-detail';

describe('RaceDetail', () => {
  let component: RaceDetail;
  let fixture: ComponentFixture<RaceDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RaceDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RaceDetail);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
