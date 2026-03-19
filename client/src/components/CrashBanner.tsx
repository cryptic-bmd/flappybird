import { useState, useEffect } from 'react';

import CrashHistory from "./CrashHistory";
import OrigamiFlappyBird from './OrigamiFlappyBird';
import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from '../utils/formatters';


const CrashBanner = () => {
  const {
    state,
    gameState,
    // fBetted,
    currentMultiplier,
    serverTimeElapsed: time,
    setCurrentTarget,
    // callCashOut
  } = useMainContext();

  const [target, setTarget] = useState(1);
	const [waiting, setWaiting] = useState(0);
  // const [cashOutCalled, setCashOutCalled] = useState(false);

  useEffect(() => {
    let myInterval: ReturnType<typeof setInterval>;
  
		if (gameState === "RUNNING") {
			const startTime = Date.now() - time;
			let currentTime;
			let currentNum;
			const getCurrentTime = () => {
				currentTime = (Date.now() - startTime) / 1000;
        // currentNum = 1 + 0.06 * currentTime
				currentNum = (
          1
          + 0.06 * currentTime
          + Math.pow((0.06 * currentTime), 2)
          - Math.pow((0.04 * currentTime), 3)
          + Math.pow((0.04 * currentTime), 4)
        );
				setTarget(currentNum);
				setCurrentTarget(currentNum);
			}
			myInterval = setInterval(() => {
				getCurrentTime();
			}, 20);
		} else if (gameState === "CRASHED") {
			setCurrentTarget(currentMultiplier);
			// eslint-disable-next-line react-hooks/set-state-in-effect
			setTarget(currentMultiplier);
		} else if (gameState === "BETTING") {
      // log("time", time);
			const startWaiting = Date.now() - time;
      // log("startWaiting", startWaiting);
			setTarget(1);
			setCurrentTarget(1);

			myInterval = setInterval(() => {
				setWaiting(Date.now() - startWaiting);
			}, 20);
		}
		return () => clearInterval(myInterval);
	}, [gameState, currentMultiplier, time, setCurrentTarget])

  return (
    <div className="mx-auto w-full relative light-game-view -mt-2 pt-4.5 md:pt-3 rounded-t-xl bg-layer3 md:px-4">
      <CrashHistory />
      <div className="min-h-63.5">
        <div className="sky relative mt-1 md:mt-4 after:content-[''] after:block after:pt-[40%] min-h-60">
            {(gameState === "RUNNING") && (
              <OrigamiFlappyBird />
            )}
            {gameState === "CRASHED" && (
              <OrigamiFlappyBird
                birdClassName="!top-[55%]"
                birdBodyClassName="!-translate-x-1/2 !-translate-y-1/2 !-rotate-x-45"
                headClassName="!rotate-x-[-20deg] !rotate-z-[-15deg]"
                leftWingClassName="!rotate-y-[60deg]"
                leftTopWingClassName="!rotate-y-[45deg]"
                rightWingClassName="!rotate-y-[-45deg]"
                rightTopWingClassName="!rotate-y-[-30deg]"
                leftTailClassName="!rotate-x-[-30deg] !rotate-z-20"
                rightTailClassName="!rotate-x-[-30deg] !rotate-z-[-20deg]"
              />
            )}
          {gameState === "BETTING" ? (
            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-2xl font-bold text-white">
              <div className="waiting">
                <div style={{ width: `${(10000 - waiting) * 100 / 10000}%` }}></div>
              </div>
            </div>
          ) : (
            <div className="absolute top-1/6 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-2xl font-bold text-white">
                <div className="flex flex-row gap-2">
                  {gameState === "CRASHED" && (
                    <>
                      <span className="text-3xl text-warning">struck!</span>
                      <span className="text-2xl">@</span>
                    </>
                  )}
                  <span className="text-3xl">
                    { formatTwoDecimalsExact(target) }x
                  </span>
                  {/* <span className="leading-[2.5rem]">X</span> */}
                </div>
            </div>
          )}
        </div>
        <div className="flex justify-end items-end m-2 sm:mt-0">
          <div className="text-secondary text-xs">Network Status</div>
          <div className="flex items-end gap-x-0.5 mb-1 ml-1.5">
            <div
              className={`w-1 rounded-[1px] h-1.5 ${
                state.pingBarCount >= 1
                  ? "bg-brand_alt shadow-[0_0_10px_rgba(36,238,137,0.7)]"
                  : "bg-layer6"
              }`}
            ></div>
            <div
              className={`w-1 rounded-[1px] h-2.25 ${
                state.pingBarCount >= 2
                  ? "bg-brand_alt shadow-[0_0_10px_rgba(36,238,137,0.7)]"
                  : "bg-layer6"
              }`}
            ></div>
            <div
              className={`w-1 rounded-[1px] h-3 ${
                state.pingBarCount >= 3
                  ? "bg-brand_alt shadow-[0_0_10px_rgba(36,238,137,0.7)]"
                  : "bg-layer6"
              }`}
            ></div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CrashBanner;
