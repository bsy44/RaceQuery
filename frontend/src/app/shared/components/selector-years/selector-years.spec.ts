import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SelectorYears } from './selector-years';

describe('SelectorYears', () => {
  let component: SelectorYears;
  let fixture: ComponentFixture<SelectorYears>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SelectorYears]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SelectorYears);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
