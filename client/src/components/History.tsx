import { useEffect, useState } from "react";
import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from "../utils/formatters";

const History = () => {
  const { state, getColorClasses } = useMainContext();
 
  const [showMore, setShowMore] = useState(false);
  const [showMore2, setShowMore2] = useState(false);
  const [selectedTab, setSelectedTab] = useState<"bets" | "history">("bets");
  const [selectedTabIsBets, setSelectedTabIsBets] = useState(true);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setSelectedTabIsBets(selectedTab === "bets");
    // log(`selectedTabIsBets: ${selectedTabIsBets}`);
  }, [selectedTab, selectedTabIsBets]);

  return (
    <div className="flex flex-col max-w-300 mx-auto">
      <div className="pb-4">
        <div className="h-8 pt-1 px-2 leading-8 text-base font-extrabold text-primary">Latest Bets</div>
        <div
          className="scroll-x tabs-title hide-scroll bg-layer3 ml-auto sm:-mt-9 w-full sm:w-auto latest-tabs"
        >
          <button
            className="tabs-btn btn-like"
            aria-selected={selectedTabIsBets}
            onClick={() => setSelectedTab("bets")}
          >
            My Bets
          </button>
          <button
            className="tabs-btn btn-like"
            aria-selected={!selectedTabIsBets}
            onClick={() => setSelectedTab("history")}
          >
            History
          </button>
          <div className="tabs-indicator"></div>
        </div>
        <div className="tabs-content">
          {selectedTab === "bets" ? (
            <div id="bets" className="min-h-72 px-2 pt-2 sm:pt-1 relative">
              <div className="relative w-full overflow-auto rounded-xl max-h-120">
                <table className="caption-bottom text-sm w-full" style={{ overflowAnchor: "none" }}>
                  <thead className="[&amp;_tr]:border-1 [&amp;_tr]:!bg-layer4">
                    <tr className="odd:bg-layer5-table border-0 transition-colors data-[state=selected]:bg-zinc-800 text-secondary">
                      <th className="py-3 px-2 sm:px-4 group text-left align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0">Bet ID</th>
                      <th className="py-3 px-2 sm:px-4 group align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0 text-center">Multiplier</th>
                      <th className="py-3 px-2 sm:px-4 group align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0 text-right">Profit</th>
                    </tr>
                  </thead>
                  <tbody className="[&amp;_tr:last-child]:border-0 group">
                    {state.myBets.slice(0, showMore ? state.myBets.length : 8).map((bet, index) => {
                      return (
                        <tr key={index} className="odd:bg-layer5-table border-0 transition-colors data-[state=selected]:bg-zinc-800">
                          <td className="first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-primary max-w-24 ellipsis overflow-hidden cursor-pointer leading-6">
                            <div className="">{bet.hash}...</div>
                          </td>
                          <td className="first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0  text-secondary text-center">
                            {formatTwoDecimalsExact(bet.cashOutMultiplier)}x
                          </td>
                          <td className={`first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-right ${ bet.winnings > 0 ? "text-brand!" : "text-warning!" }`}>
                            <span className="inline-flex items-center gap-0 whitespace-nowrap">
                              <span>
                                {bet.winnings > 0 ? "+" : "-"}${formatTwoDecimalsExact(bet.winnings || bet.betAmount)}
                              </span>
                              {/* <div className="rounded-full inline-flex shrink-0 items-center justify-center leading-6 !ml-1 !size-4">
                                <img src="/coin/USD.rect.png" className="w-4 h-4" />
                              </div> */}
                            </span>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
              {state.myBets.length > 0 && (
                <div className="bottom-1 left-0 right-0 pointer-events-none">
                  <button
                    className="button button-second mx-auto gap-2 my-2 h-8 px-2 bg-none bg-button_bright pointer-events-auto"
                    type="button"
                    onClick={() => { setShowMore(!showMore); }}
                  >
                    <span>{showMore ? "Show Less" : "Show More"}</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div id="crash-history" className="relative">
              <div className="mt-2">
                <div className="min-h-72 px-2 pt-2 sm:pt-1 relative ">
                  <div className="relative w-full overflow-auto max-h-160 rounded-xl sm:max-h-120">
                    <table className="w-full caption-bottom text-sm" style={{ overflowAnchor: "none" }}>
                      <thead className="[&amp;_tr]:border-1 [&amp;_tr]:!bg-layer4">
                        <tr className="odd:bg-layer5-table border-0 transition-colors data-[state=selected]:bg-zinc-800 text-secondary">
                          <th className="py-3 px-2 sm:px-4 group text-left align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0">Game ID</th>
                          <th className="py-3 px-2 sm:px-4 group align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0 text-center">Result</th>
                          <th className="py-3 px-2 sm:px-4 group align-middle font-semibold text-zinc-400 [&amp;:has([role=checkbox])]:pr-0 text-right">Hash</th>
                        </tr>
                      </thead>
                      <tbody className="[&amp;_tr:last-child]:border-0 group">
                        {state.gameHistory.slice(0, showMore2 ? state.gameHistory.length : 8).map((game, index) => {
                          const { bg } = getColorClasses(game.crashPoint);
                          return (
                            <tr key={index} className="odd:bg-layer5-table border-0 transition-colors data-[state=selected]:bg-zinc-800">
                              <td className="first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-zinc-50 cursor-pointer">
                                <span className="inline-flex items-center gap-1">
                                  <span className={`w-2 h-2 rounded-full ${bg}`}></span>
                                  <span className="text-primary hover:underline leading-6">{game.gameID}</span>
                                </span>
                              </td>
                              <td className="first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-center text-secondary">
                                {formatTwoDecimalsExact(game.crashPoint)}x
                              </td>
                              <td className="first:rounded-l-lg last:rounded-r-lg py-2.5 px-2 sm:px-4 align-middle [&amp;:has([role=checkbox])]:pr-0 text-right text-secondary max-w-40 truncate">
                                {game.gameHash}...
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                  {state.gameHistory.length > 0 && (   
                    <div className="bottom-1 left-0 right-0 pointer-events-none">
                      <button
                        className="button button-second mx-auto gap-2 my-2 h-8 px-2 bg-none bg-button_bright pointer-events-auto"
                        type="button"
                        onClick={() => { setShowMore2(!showMore2); }}
                      >
                        <span>{showMore2 ? "Show Less" : "Show More"}</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default History;
