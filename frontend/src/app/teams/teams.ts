import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import {NgIf, NgOptimizedImage} from '@angular/common';
import { TEAMS_INFO } from '../shared/teams-info'

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
  selectedYear: number = new Date().getFullYear();

  constructor(private http: HttpClient) {}

  ngOnInit() {
    const currentYear = new Date().getFullYear();
    this.years = Array.from({ length: currentYear - 2022 + 1 }, (_, i) => 2022 + i).reverse();

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
