import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NATIONALITY_TO_ISO } from '../../nationalities';

@Component({
  selector: 'app-table-standing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './table-standing.html',
  styleUrls: ['./table-standing.css']
})
export class TableStanding {
  @Input() columns: string[] = [];
  @Input() data: any[] = [];

  getDriverFlag(driverNationality: string): string {
    return NATIONALITY_TO_ISO[driverNationality] || 'un';
  }
}
