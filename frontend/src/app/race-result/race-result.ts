import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { SessionResultTableComponent } from '../shared/components/table-results/table-results';
import { TEAMS_INFO } from '../shared/teams-info'
import {RaceInfo} from '../shared/components/race-info/race-info';

@Component({
  imports: [
    FormsModule,
    SessionResultTableComponent,
    RaceInfo
  ],
  selector: 'app-race-result',
  styleUrls: ['./race-result.css'],
  templateUrl: './race-result.html'
})
export class RaceResult implements OnInit {
  round!: number;
  season!: number;
  eventInfo!: string;
  raceList: RaceResultModel[] = [];
  isLoading = false;
  race: any = null;
  sessionCode: string = 'R';
  sessions: string[] = [];
  sessionMapping: { [key: string]: string } = {
    'Essais libres 1': 'FP1',
    'Essais libres 2': 'FP2',
    'Essais libres 3': 'FP3',
    'Qualification': 'Q',
    'Qualification sprint': 'SQ',
    'Course sprint': 'S',
    'Course': 'R'
  };
  winner:any;
  pole: any;
  fastestLap : any;

  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private router:Router) {}

  ngOnInit() {
    const nav = this.router.lastSuccessfulNavigation;
    this.round = nav?.extras?.state?.['round'] || null;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    this.eventInfo = this.route.snapshot.paramMap
      .get('gpName')!
      .replace(/-/g, ' ')
      .toUpperCase();

    this.httpClient.get<any>(`http://127.0.0.1:5000/events/${this.season}/${this.round}`)
      .subscribe(result => {
        this.race = result;

        if (this.race.event_format === 'sprint_qualifying') {
          this.sessions = [
            'Essais libres 1',
            'Qualification sprint',
            'Qualification',
            'Course sprint',
            'Course'
          ];
        } else {
          this.sessions = [
            'Essais libres 1',
            'Essais libres 2',
            'Essais libres 3',
            'Qualification',
            'Course'
          ];
        }

        this.sessionCode = this.sessionMapping['Course'];
        this.getSessionResult();
      });
  }

  getSessionResult() {
    if (!this.sessionCode) return;

    const session = this.sessionCode.trim().toUpperCase();
    this.isLoading = true;

    this.httpClient
      .get<any>(`http://127.0.0.1:5000/events/${session}-results/${this.season}/${this.round}`)
      .subscribe({
        next: (response: any) => {
          if (response && Array.isArray(response.results)) {
            this.winner = response.winner || null;
            this.pole = response.poleman || null;
            this.fastestLap = response.fastestLap || null;
            this.raceList = response.results.map((r: RaceResultModel) => ({
              ...r
            }));
          } else {
            this.raceList = [];
            this.winner = null;
            this.pole = null;
            this.fastestLap = null;
          }
          this.isLoading = false;
        },
        error: err => {
          console.error('Erreur de chargement des résultats :', err);
          this.raceList = [];
          this.winner = null;
          this.pole = null;
          this.fastestLap = null;
          this.isLoading = false;
        }
      });
  }

  protected readonly TEAMS_INFO = TEAMS_INFO;
}
