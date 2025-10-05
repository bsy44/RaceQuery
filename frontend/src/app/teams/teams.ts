import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {NgIf, NgOptimizedImage} from '@angular/common';

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

interface Team {
  constructor: string;
  points: string;
  teamLogo?: string;
}


@Component({
  selector: 'app-teams',
  templateUrl: './teams.html',
  imports: [
    FormsModule,
    NgOptimizedImage,
    NgIf
  ],
  styleUrls: ['./teams.css']
})
export class Teams implements OnInit {
  teamList: any[] = [];
  years: number[] = [];
  selectedYear: number = new Date().getFullYear(); // année actuelle par défaut

  constructor(private http: HttpClient) {}

  ngOnInit() {
    const currentYear = new Date().getFullYear();
    this.years = Array.from({ length: currentYear - 2022 + 1 }, (_, i) => 2022 + i).reverse();

    // Charge la saison actuelle au démarrage
    this.getTeams();
  }

  getTeams() {
    this.http
      .get<any>(`http://127.0.0.1:5000/standings/teams/${this.selectedYear}`)
      .subscribe((result) => {

        // result est déjà un tableau
        this.teamList = (result || []).map((team: Team) => {
              const constructor = team.constructor;
              const teamLogo = TEAMS_INFO[constructor]?.logo || '';
              return { ...team, teamLogo };
        });
      });
  }

}
