import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-session-result-table',
  standalone: true,
  imports: [],
  templateUrl: './table-results.html',
  styleUrls: ['./table-results.css']
})
export class SessionResultTableComponent {
  @Input() sessionCode!: string;
  @Input() results: any[] = [];

  isQualifying() {
    return this.sessionCode?.includes('Q');
  }
  isPractice() {
    return this.sessionCode?.includes('FP');
  }
  isRaceOrSprint() {
    return this.sessionCode?.includes('R') || this.sessionCode?.includes('S');
  }
}
