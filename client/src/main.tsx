import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { retrieveLaunchParams } from '@telegram-apps/sdk-react';

import App from './App.tsx'
import EnvUnsupported from './components/EnvUnsupported.tsx';
import { init } from './init.ts';
import { DEV } from './config.ts';

import './index.css'
// Include Telegram UI styles first to allow our code override the package CSS.
import '@telegram-apps/telegram-ui/dist/styles.css';


const root = createRoot(document.getElementById('root')!);

try {
  const launchParams = retrieveLaunchParams();
  const { tgWebAppPlatform: platform } = launchParams;
  const debug = (launchParams.tgWebAppStartParam || '').includes('platformer_debug') || DEV;

  // Configure all application dependencies.
  await init({
    debug,
    eruda: debug && ['ios', 'android'].includes(platform),
    mockForMacOS: platform === 'macos',
  })
    .then(() => {
      root.render(
        DEV ? (
          <StrictMode>
            <App/>
          </StrictMode>
        ) : (
          <App/>
        )
      );
    });
// eslint-disable-next-line @typescript-eslint/no-unused-vars
} catch (e) {
  root.render(<EnvUnsupported/>);
}
