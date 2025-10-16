import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, Router } from '@angular/router';
import { RaceResultModel } from '../shared/models/raceResult.model';
import { FormsModule } from '@angular/forms';
import { SessionResultTableComponent } from '../shared/components/table-results/table-results';
import { TEAMS_INFO } from '../shared/teams-info'

@Component({
  imports: [
    FormsModule,
    SessionResultTableComponent
  ],
  selector: 'app-race-result',
  styleUrls: ['./race-result.css'],
  templateUrl: './race-result.html'
})
export class RaceResult implements OnInit {
  round!: number;
  season!: number;
  eventInfo!: string;
  raceList: any[] = [];
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

  constructor(private httpClient: HttpClient, private route: ActivatedRoute, private router:Router) {}

  ngOnInit() {
    const nav = this.router.lastSuccessfulNavigation;
    this.round = nav?.extras?.state?.['round'] || null;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    this.eventInfo = this.route.snapshot.paramMap.get('gpName')!.replace('-', ' ').toUpperCase();

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
      .get<RaceResultModel[]>(`http://127.0.0.1:5000/events/${session}-results/${this.season}/${this.round}`)
      .subscribe({
        next: (response: any[]) => {
          if (Array.isArray(response)) {
            this.raceList = response.map(r => {
              return {
                ...r,
                teamLogo: TEAMS_INFO[r.team]?.logo || ''
              };
            });
          } else {
            this.raceList = [];
          }
          this.isLoading = false;
        }
      });
  }
}
