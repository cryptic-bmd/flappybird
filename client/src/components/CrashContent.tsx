import BetControls from "./BetControls";
import BetLog from "./BetLog";
import CrashBanner from "./CrashBanner";
import History from "./History";


const CrashContent = () => {
  return (
    <div
      className="scroll-y dialog-content"
    >
      <div className="scroll-container">
        <div id="game-full-container" className="max-w-308 mx-auto w-full sm:px-4 sm:pb-5 transition-all duration-200 @container">
          <div id="game-full-layout" className="mx-auto py-3 sm:py-0 grid-cols-1">
            <div id="game-view-control" className="flex flex-col h-full">
              <div className="grid grid-cols-1 grow bg-layer2 relative rounded-lg @4xl:pb-0 @4xl:grid-cols-[minmax(22.5rem,22.5rem)_auto] @4xl:h-full @4xl:flex!">
                <div className="order-1 col-span-full bg-layer3 flex flex-col rounded-t-xl @4xl:order-2 @4xl:col-span-1 @4xl:relative @4xl:pt-2 @4xl:rounded-tl-none @4xl:rounded-tr-xl @4xl:h-full h-auto @4xl:grow! @4xl:min-h-168 overflow-hidden @4xl:overflow-x-scroll rounded-xl!">
                  <CrashBanner />
                  <BetControls index="f" />
                </div>
              </div>
            </div>
            <BetLog />
          </div>
          <History />
        </div>
      </div>
    </div>
  )
}

export default CrashContent;
