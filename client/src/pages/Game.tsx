import CrashContent from '../components/CrashContent.tsx';
import Dialog from '../components/Dialog.tsx';
import Header from '../components/Header.tsx';
import MainProvider from '../context/MainContext.tsx';
import { Page } from '../components/Page.tsx';


const GameContent: React.FC = () => {
  return (
    <>
      <Dialog>
        <Header />
        <CrashContent />
      </Dialog>
    </>
  )
};

const Game: React.FC = () => {
  return (
    <Page>
      <MainProvider>
        <GameContent />
      </MainProvider>
    </Page>
  );
};

export default Game;
