import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { NATIONALITY_TO_ISO } from '../../nationalities';

@Component({
  selector: 'app-table-standing',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './table-standing.html',
  styleUrls: ['./table-standing.css']
})
export class TableStanding implements OnInit {
  @Input() columns: string[] = [];
  @Input() data: any[] = [];
  @Input() rowTemplate!: any;
  @Input() years!: number[];
  @Input() selectedYear: number = new Date().getFullYear();

  @Output() selectedYearChange = new EventEmitter<number>();

  ngOnInit(): void {
    const currentYear = new Date().getFullYear();
    if (!this.years) {
      this.years = Array.from({ length: currentYear - 2022 + 1 }, (_, i) => 2022 + i).reverse();
    }
  }

  onYearChange(newYear: number) {
    this.selectedYear = newYear;
    this.selectedYearChange.emit(newYear);
  }

  getDriverFlag(driverNationality: string): string {
    return NATIONALITY_TO_ISO[driverNationality] || 'un';
  }
}
