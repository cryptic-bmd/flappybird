import { useState } from "react";

import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from "../utils/formatters";


const BetLog = () => {
  const {
    noOfBets,
    totalBetAmount,
    noOfCashouts,
    bettedUsers
  } = useMainContext();
  const [showMore, setShowMore] = useState(false);

  return (
    <div className="order-3 col-span-8 @4xl:order-2 @4xl:col-span-3 @4xl:hidden">
      <div className="p-2 rounded-xl bg-layer4 relative mt-2 @4xl:mt-0 @4xl:ml-2 overflow-hidden grow">
        <div className="flex items-center justify-between bg-layer3 p-2 rounded-lg h-9">
          <div className="flex items-center justify-center">
            <div className="mr-2">
              <svg xmlns="http://www.w3.org/2000/svg" width="13" height="14" viewBox="0 0 13 14" fill="none">
                <circle cx="6.5" cy="6.78613" r="6.5" fill="#23EE88" fillOpacity="0.2"></circle>
                <circle cx="6.5" cy="6.78613" r="2.36328" fill="#23EE88"></circle>
              </svg>
            </div>
            <div className="font-extrabold font-mono">
              {noOfCashouts}/{noOfBets}&nbsp;Players
            </div>
          </div>
          <div className="flex font-semibold font-mono">
            $&nbsp;{formatTwoDecimalsExact(totalBetAmount)}
          </div>
        </div>
        <div className="bg-layer4 p-1">
          <div className="flex text-left whitespace-nowrap">
            <div className="font-normal text-secondary py-2 w-2/5 truncate">Player</div>
            <div className="font-normal text-secondary py-2 text-left w-1/5">Cashout</div>
            <div className="font-normal text-secondary py-2 text-right w-2/5">Amount</div>
          </div>
        </div>
        <div className="p-1 pt-0 overflow-y-auto h-130 sm:h-[35.2rem] mb-0 relative" style={{ maskImage: "linear-gradient(to top, transparent 0%, black 10%)" }}>
          <div className="size-full relative">
            <div className="h-auto">
              {
                bettedUsers.slice(0, showMore ? bettedUsers.length : 10).map((user, index) => (
                  <div key={index} className="flex h-10 items-center w-full justify-start font-bold">
                    <div className="flex items-center w-2/5 text-secondary">
                      <a className="truncate inactive">{user.userHash}</a>
                    </div>
                    <div className="w-1/5 text-left">
                      <div className="pl-1 whitespace-nowrap">
                        { user.cashedOut && user.target > 0 ? (
                          `${formatTwoDecimalsExact(user.target)}x`
                        ) : "-" }
                      </div>
                    </div>
                    <div className="w-2/5 flex">
                      <div
                        className={`w-full flex justify-end items-center ${
                          user.cashedOut ? "text-success" : "text-gray-300"
                        }`}
                      >
                        {/* <img alt="" className="inline-block size-4 mr-1" src="/coin/USD.rect.png" /> */}
                        <div className="truncate">
                          $&nbsp;{formatTwoDecimalsExact(user.betAmount)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              }
            </div>
          </div>
        </div>
        {bettedUsers.length > 0 && (
          <div className="absolute left-1/2 transform -translate-x-1/2 bottom-0 w-full mb-1.5">
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
    </div>
  )
}

export default BetLog;
