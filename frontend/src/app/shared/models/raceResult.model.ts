import { Driver } from './driver.model';
import { Team } from './team.model';

export interface RaceResultModel {
  Results: {
    Constructor: Team;
    Driver: Driver
    FastestLap:{
      Time: {
        time: string;
      }
      rank: string
    };
    Time: {
      millis: string;
      time: string;
    };
    grid: string;
    laps: string;
    points: string;
    position: string;
    status: string;
  }[];
  race: {
    Circuit: {
      circuitId: string;
      circuitName: string;
    };
    raceName: string;
  }
}
