import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { TEAMS_INFO } from '../shared/teams-info';
import { TableStanding } from '../shared/components/table-standing/table-standing';
import { SelectorYears } from '../shared/components/selector-years/selector-years';

@Component({
  selector: 'app-drivers',
  templateUrl: './drivers.html',
  imports: [
    FormsModule,
    TableStanding,
    SelectorYears
  ],
  styleUrls: ['./drivers.css']
})
export class Drivers implements OnInit {
  driverList: any[] = [];
  years: number[] = [];
  selectedYear: number = new Date().getFullYear();

  constructor(private http: HttpClient) {}

  ngOnInit() {
    const currentYear = new Date().getFullYear();
    this.years = Array.from({ length: currentYear - 2024 + 1 }, (_, i) => 2024 + i).reverse();
    this.getDrivers();
  }

  columns = ['Pos', 'Pilote', 'Ecurie', 'Points'];

  getDrivers() {
    this.http
      .get<any>(`http://127.0.0.1:5000/drivers/standings/${this.selectedYear}`)
      .subscribe((result) => {
        this.driverList = result.DriverStandings.map((driver: any, i: number) => {
          const teamName = driver.constructor[0];
          const teamLogo = TEAMS_INFO[teamName]?.logo || '';

          return {
            Pos: i + 1,
            driver: {
              fullName: driver.driver.fullName,
              nationality: driver.driver.nationality
            },
            constructor: teamName,
            teamLogo,
            Points: +driver.points,
            PointsDiff: i > 0 ? +driver.points_diff : 0
          };
        });
      });
  }
}
