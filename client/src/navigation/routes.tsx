import type { ComponentType, JSX } from 'react';

import Game from '../pages/Game.tsx';


interface Route {
  path: string;
  Component: ComponentType;
  title?: string;
  icon?: JSX.Element;
}

export const routes: Route[] = [
  { path: '/', Component: Game },
];
