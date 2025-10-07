import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import {FormsModule} from '@angular/forms';
import { TEAMS_INFO } from '../shared/teams-info'
import { TableStanding } from '../shared/components/table-standing/table-standing';
import { SelectorYears } from '../shared/components/selector-years/selector-years';

interface Team {
  constructor: string;
  points: string;
  teamLogo?: string;
  points_diff: string;
}

@Component({
  selector: 'app-teams',
  templateUrl: './teams.html',
  imports: [
    FormsModule,
    TableStanding,
    SelectorYears
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
    this.years = Array.from({ length: currentYear - 2024 + 1 }, (_, i) => 2024 + i).reverse();

    this.getTeams();
  }

    columns = ['Pos', 'Ecurie', 'Points'];


  getTeams() {
    this.http
      .get<any>(`http://127.0.0.1:5000/standings/teams/${this.selectedYear}`)
      .subscribe((result) => {

        this.teamList = (result || []).map((team: Team, i: number) => {
          const constructor = team.constructor;
          const teamLogo = TEAMS_INFO[constructor]?.logo || '';
          return {
            Pos: i + 1,
            constructor: constructor,
            teamLogo,
            Points: +team.points,
            PointsDiff: i > 0 ? +team.points_diff : 0
          };
        });
      });
  }
}
