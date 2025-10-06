import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableStanding } from './table-standing';

describe('TableStanding', () => {
  let component: TableStanding;
  let fixture: ComponentFixture<TableStanding>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableStanding]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableStanding);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
