import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RaceInfo } from './race-info';

describe('RaceInfo', () => {
  let component: RaceInfo;
  let fixture: ComponentFixture<RaceInfo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RaceInfo]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RaceInfo);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
