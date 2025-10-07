import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-year-selector',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './selector-years.html',
  styleUrls: ['./selector-years.css']
})
export class SelectorYears implements OnInit {
  @Input() years: number[] = [];
  @Input() selectedYear: number = new Date().getFullYear();
  @Output() selectedYearChange = new EventEmitter<number>();

  ngOnInit() {
    if (!this.years || this.years.length === 0) {
      const currentYear = new Date().getFullYear();
      this.years = Array.from({ length: currentYear - 2024 + 1 }, (_, i) => 2024 + i).reverse();
    }
  }

  onChange(newYear: number) {
    this.selectedYear = +newYear;
    this.selectedYearChange.emit(this.selectedYear);
  }

}
