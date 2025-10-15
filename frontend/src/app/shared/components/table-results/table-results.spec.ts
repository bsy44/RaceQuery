import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TableResults } from './table-results';

describe('TableResults', () => {
  let component: TableResults;
  let fixture: ComponentFixture<TableResults>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TableResults]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TableResults);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
