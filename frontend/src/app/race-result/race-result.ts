import {Component, OnInit} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { NgForOf, NgIf} from '@angular/common';
import { RaceResultModel } from '../shared/models/raceResult.model';

@Component({
  selector: 'app-race-result',
  templateUrl: './race-result.html',
  imports: [
    NgIf,
    NgForOf
  ],
  styleUrls: ['./race-result.css']
})
export class RaceResult implements OnInit{
  round!: number;
  season!: number;
  raceList: any[] = []
  isLoading = false;
  race: any = null;

  constructor(private httpClient: HttpClient, private route: ActivatedRoute) {}

  ngOnInit() {
    this.round = +this.route.snapshot.paramMap.get('round')!;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    this.getRaceResult();
  }

  getRaceResult() {
    this.isLoading = true;

    this.httpClient
      .get<RaceResultModel[]>(`http://127.0.0.1:5000/races/results/${this.season}/${this.round}`)
      .subscribe({
        next: (response: RaceResultModel[]) => {
          const raceData = response[0];
          this.race = raceData.race;
          this.raceList = raceData.Results;
          this.isLoading = false;
        },
        error: (err) => {
          console.error('Erreur de chargement des résultats :', err);
          this.isLoading = false;
        },
      });
  }

}
