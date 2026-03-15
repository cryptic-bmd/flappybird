import { Navigate, Route, Routes, HashRouter } from 'react-router-dom';
import { routes } from './navigation/routes.tsx';
import AuthProvider from './context/AuthContext.tsx';

const App = () => {
  return (
    <AuthProvider>
      <HashRouter>
        <Routes>
          {routes.map((route) => <Route key={route.path} {...route} />)}
          <Route path="*" element={<Navigate to="/"/>}/>
        </Routes>
      </HashRouter>
    </AuthProvider>
  );
};

export default App;
