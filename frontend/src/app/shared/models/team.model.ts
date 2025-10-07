export interface Constructor {
  constructor: {
    constructorId: string;
    name: string;
    nationality: string;
    teamLogo?: string;
  };
  position: string;
  points: string;
  points_diff: string;
  wins: string;
}
