import { type PropsWithChildren, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

import { hideBackButton, onBackButtonClick, showBackButton } from '@telegram-apps/sdk-react';

import Loading from './Loading.tsx';
import { useAuthContext } from '../context/authContext.ts';


export function Page({ children, back = true }: PropsWithChildren<{
  /**
   * True if it is allowed to go back from this page.
   */
  back?: boolean
}>) {
  const navigate = useNavigate();
  const { authLoading } = useAuthContext();

  useEffect(() => {
    if (back) {
      showBackButton();
      return onBackButtonClick(() => {
        navigate(-1);
      });
    }
    hideBackButton();
  }, [back, navigate]);

  useEffect(() => {
    // log(`authLoading: ${authLoading}`);
  }, [authLoading])

  return authLoading ? <Loading /> : <>{children}</>;
}
