import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {NgIf, NgOptimizedImage} from '@angular/common';
import { NATIONALITY_TO_ISO } from '../shared/nationalities';

const TEAMS_INFO: { [key: string]: { logo: string } } = {
  "Red Bull": { logo: "logos/rbr-logo.avif" },
  "RB F1 Team": { logo: "logos/vcrb-logo.avif" },
  "Mercedes": { logo: "logos/mercedes-logo.avif" },
  "McLaren": { logo: "logos/mclaren-logo.avif" },
  "Ferrari": { logo: "logos/ferrari-logo.avif" },
  "Alpine F1 Team": { logo: "logos/alpine-logo.avif" },
  "Williams": { logo: "logos/williams-logo.avif" },
  "Aston Martin": { logo: "logos/aston-martin-logo.avif" },
  "Haas F1 Team": { logo: "logos/haas-logo.avif" },
  "Sauber": { logo: "logos/kick-sauber-logo.avif" },
  "Racing Point": { logo: "logos/Racing_Point.svg" },
  "AlphaTauri": { logo: "logos/alphaTauri.svg.png" },

};

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
