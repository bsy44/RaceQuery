import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {NgIf, NgOptimizedImage} from '@angular/common';
import { NATIONALITY_TO_ISO } from '../shared/nationalities';
import { TEAMS_INFO } from '../shared/teams-info';


interface Driver {
  driver: { fullName: string; nationality: string };
  constructor: string[];
  points: string;
  teamLogo?: string;
}


@Component({
  selector: 'app-drivers',
  templateUrl: './drivers.html',
  imports: [
    FormsModule,
    NgOptimizedImage,
    NgIf
  ],
  styleUrls: ['./drivers.css']
})
export class Drivers implements OnInit {
  driverList: any[] = [];
  years: number[] = [];
  selectedYear: number = new Date().getFullYear(); // année actuelle par défaut

  constructor(private http: HttpClient) {}

  ngOnInit() {
    // Remplit la liste des années de 2020 → année actuelle
    const currentYear = new Date().getFullYear();
    this.years = Array.from({ length: currentYear - 2022 + 1 }, (_, i) => 2022 + i).reverse();

    // Charge la saison actuelle au démarrage
    this.getDrivers();
  }

  getDrivers() {
  this.http
    .get<any>(`http://127.0.0.1:5000/standings/drivers/${this.selectedYear}`)
    .subscribe((result) => {
      this.driverList = result.DriverStandings.map((driver: Driver) => {
        const teamName = driver.constructor[0];
        const teamLogo = TEAMS_INFO[teamName]?.logo || '';

        return {
          ...driver,
          teamLogo
        };
      });
    });
  }

  getDriverFlag(driverNationality: string): string {
    return NATIONALITY_TO_ISO[driverNationality] || 'un';
  }

}
