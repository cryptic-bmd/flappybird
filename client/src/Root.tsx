import { useEffect } from 'react';

import { setMiniAppHeaderColor, setMiniAppBottomBarColor } from '@telegram-apps/sdk-react';
import { ToastContainer, Bounce } from 'react-toastify';

import App from './App.tsx';
import ErrorBoundary from './components/ErrorBoundary.tsx';


const ErrorBoundaryError =({ error }: { error: unknown }) => {
  return (
    <div>
      <p>An unhandled error occurred:</p>
      <blockquote>
        <code>
          {error instanceof Error
            ? error.message
            : typeof error === 'string'
              ? error
              : JSON.stringify(error)}
        </code>
      </blockquote>
    </div>
  );
}

const Root = () => {
  useEffect(() => {
    if (setMiniAppHeaderColor.isAvailable() && setMiniAppHeaderColor.supports.rgb()) {
      setMiniAppHeaderColor("#151e27");
    }
    if (setMiniAppBottomBarColor.isAvailable()) {
      setMiniAppBottomBarColor("#151e27");
    }
  }, []);

  return (
    <ErrorBoundary fallback={ErrorBoundaryError}>
      <App />
      <ToastContainer
        className="w-[80%]! top-4! left-1/2! -translate-x-1/2!"
        position="top-center"
        autoClose={5000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick={false}
        rtl={false}
        pauseOnFocusLoss
        draggable
        pauseOnHover
        theme="dark"
        transition={Bounce}
      />
    </ErrorBoundary>
  );
}

export default Root;
