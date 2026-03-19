import { useEffect, useState } from 'react';
import * as Slider from '@radix-ui/react-slider';

import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from '../utils/formatters';
import { log } from '../utils/logger';


const BetControls = ({ index = 'f' }: { index: "f" | "s" }) => {
  const {
    state,
    gameState,
    fToBet,
    fBetted,
    minBet,
    maxBet,
    currentTarget,
    showBetAmountNote,
    update,
    updateUserBetState,
    callCashOut,
    setShowPopOverLay,
    setShowBetAmountNote,
  } = useMainContext();

  // const fToBet = fToBet;
  // const fBetted = fBetted;
  const betAmount = state.userInfo.f.betAmount;
  const target = state.userInfo.f.target;

  const [myBetAmount, setMyBetAmount] = useState(betAmount);
  const [cashOutTarget, setCashOutTarget] = useState(target);
  const [showRange, setShowRange] = useState(false);

  const onChangeBlur = (e: number, type: 'cashOutAt' | 'Decrease' | 'Increase' | 'SingleAmount') => {
		const stateValue = state;
		if (type === "cashOutAt") {
      log(`e: ${e}`);
			if (e < 1.01) {
				// eslint-disable-next-line react-hooks/immutability
				stateValue.userInfo[index]['target'] = 1.01;
				setCashOutTarget(1.01);
			} else {
        // const t = Math.round(e * 100) / 100;
				stateValue.userInfo[index]['target'] = e;
				setCashOutTarget(e);
			}
		} else {
      const key = `${index}${type}` as keyof typeof stateValue;
      if (e < 0.1) {
        if (key in stateValue) {
          // @ts-expect-error: dynamic assignment, ensure type safety elsewhere
          // eslint-disable-next-line react-hooks/immutability
          stateValue[key] = 0.1;
        }
      } else {
        if (key in stateValue) {
          // @ts-expect-error: dynamic assignment, ensure type safety elsewhere
          stateValue[key] = Math.round(e * 100) / 100;
        }
      }
		}
		update(stateValue);
	}

  const changeBetAmount = (newBetAmount: number) => {
    // log(`state.userInfo.f.target: ${state.userInfo.f.target}`);
    // log(`state.userInfo.f.betAmount: ${state.userInfo.f.betAmount}`);;
    // if (newBetAmount > maxBet) {
    //   newBetAmount = maxBet;
    // } else if (newBetAmount < minBet) {
    //   newBetAmount = minBet;
    // }
    const attrs = state;
    // eslint-disable-next-line react-hooks/immutability
    attrs.userInfo[index]['betAmount'] = newBetAmount;
    update(attrs);
    // setTimeout(() => {
    //   log(`state.userInfo.f.target 1: ${state.userInfo.f.target}`);
    //   log(`state.userInfo.f.betAmount,1: ${state.userInfo.f.betAmount}`);
    // }, 3000);
  }

  const onBetAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    changeBetAmount(Number(e.target.value));
  }

  const onBetClick = (s: boolean) => {
    // log(`${`${index}ToBet`}: ${s}`);
		updateUserBetState({ [`${index}ToBet`]: s })
	}

  useEffect(() => {
		setMyBetAmount(betAmount);
	}, [betAmount])

  useEffect(() => {
    setCashOutTarget(target);
  }, [target])

  return (
    <div className="col-span-full order-2 flex flex-col gap-3 bg-layer4 @4xl:order-0 @4xl:rounded-tl-xl @4xl:pt-0.5 @4xl:h-full @4xl:overflow-y-auto rounded-t-none! @4xl:col-span-8! @4xl:max-h-full pt-0!">
      <div data-orientation="horizontal" id="tabs-cl-68" className="flex flex-col relative @4xl:h-full @4xl:overflow-x-hidden!">
        <div id="tabs-cl-68-content-manual" role="tabpanel" data-orientation="horizontal" data-selected="" className="mt-0 @4xl:relative z-100 @4xl:overflow-auto" aria-labelledby="tabs-cl-68-trigger-manual">
          <div className="flex flex-col gap-3 px-3 mb-2 md:mb-3 mt-2 @4xl:py-3 relative z-100" style={{ opacity: 1, transform: "translateX(var(--motion-translateX))" } as React.CSSProperties}>
            <div className="flex flex-col @4xl:flex-row gap-3 justify-between">
              <div id="bet-amount-input" className="w-full @4xl:w-1/2">
                <div role="group" id="NumberField-cl-69" className="w-full">
                  <div className="flex items-center mb-1 justify-between">
                    <label id="NumberField-cl-69-label" className="peer-disabled:cursor-not-allowed peer-disabled:opacity-40 text-secondary data-invalid:text-secondary px-1 flex items-center h-4.5 pl-1 mr-1 text-sm font-extrabold">
                      Amount
                    </label>
                    <div className="grow flex items-center">
                      <button
                        type="button"
                        aria-haspopup="dialog"
                        aria-expanded="false"
                        data-closed=""
                        className="focus-visible:outline-none size-4"
                        onClick={() => setShowBetAmountNote(!showBetAmountNote)}
                      >
                        <svg className="icon size-4 text-brand_alt" viewBox="0 0 32 32">
                          <path d="M12.926 30c-6.034 0-10.925-4.892-10.925-10.925v-6.149c0-6.034 4.892-10.925 10.925-10.925h6.149c6.033 0 10.925 4.892 10.925 10.925v6.149c0 6.034-4.892 10.925-10.925 10.925h-6.149zM12.926 27.62h6.149c4.721 0 8.546-3.827 8.546-8.546v-6.149c0-4.721-3.827-8.546-8.546-8.546h-6.149c-4.721 0-8.546 3.827-8.546 8.546v6.149c0 4.721 3.827 8.546 8.546 8.546zM16.001 12.841c-0.713 0-1.303-0.53-1.396-1.217l-0.012-0.191v-0.090c0-0.778 0.631-1.409 1.409-1.409 0.713 0 1.303 0.53 1.396 1.217l0.012 0.191v0.090c0 0.778-0.631 1.409-1.409 1.409zM16.001 22.874c-0.713 0-1.303-0.53-1.396-1.217l-0.012-0.191v-6.047c0-0.778 0.631-1.409 1.409-1.409 0.713 0 1.303 0.53 1.396 1.217l0.012 0.191v6.047c0 0.779-0.631 1.409-1.409 1.409z"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div className="relative">
                    <div className="input font-extrabold pr-1 sm:pr-0.75 nowidth-input rounded-lg">
                      {fToBet || fBetted ?
                        <input size={20} inputMode="decimal" type="number" value={myBetAmount} readOnly ></input>
                        :
                        <input 
                          size={20}
                          inputMode="decimal"
                          type="number" 
                          value={myBetAmount}
                          onChange={(e) => onBetAmountChange(e)}
                        ></input>
                      }
                      {/* <div className="rounded-full inline-flex shrink-0 size-6 items-center justify-center leading-6 order-first scale-[1.2]">
                        <img src="/USD.png" className="w-4 h-4"/>
                      </div> */}
                      <div className="flex items-center gap-1">
                        <button 
                          className="button button-input text-primary h-10 sm:h-8 w-12.5 rounded-md"
                          type="button"
                          onClick={() => changeBetAmount(myBetAmount / 2)}
                        >
                          1/2
                        </button>
                        <button
                          className="button button-input text-primary h-10 sm:h-8 w-12.5 rounded-md"
                          type="button"
                          onClick={() => changeBetAmount(myBetAmount * 2)}
                        >
                          2×
                        </button>
                        <button
                          className="button button-input text-primary h-10 sm:h-8 w-12.5 rounded-md"
                          type="button"
                          onClick={() => setShowRange(!showRange)}
                        >
                          <div className="flex flex-col">
                            <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" className="size-4 rotate-90">
                              <path fill="currentColor" d="M19.691 5.6 9.291 16l10.4 10.4 3.018-3.017L15.326 16l7.383-7.382z"></path>
                            </svg>
                            <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" className="size-4 -rotate-90">
                              <path fill="currentColor" d="M19.691 5.6 9.291 16l10.4 10.4 3.018-3.017L15.326 16l7.383-7.382z"></path>
                            </svg>
                          </div>
                        </button>
                        <div className={`${!showRange ? "hidden" : ""} absolute top-12 right-0 w-full sm:top-10 bg-layer6 rounded-lg z-1000`}>
                          <div className="flex flex-row justify-center items-stretch rounded-lg w-full bg-layer6 dark:bg-layer6 focus-visible:outline-none">
                            <button
                              className="button focus-visible:outline-none h-10 bg-button_bright rounded-r-none"
                              type="button"
                              onClick={() => changeBetAmount(minBet)}
                            >
                              Min
                            </button>
                            <div
                              role="group"
                              id="slider-cl-82"
                              data-orientation="horizontal"
                              className="relative flex w-full touch-none select-none flex-col items-center light-darkness flex-1 self-center mx-2 bg-none!"
                            >
                              <div data-orientation="horizontal" className="relative h-2.5 w-full grow rounded-full bg-layer4 light-darkness">
                                <div data-orientation="horizontal" className="absolute h-full bg-linear-to-r from-brand to-brand_alt rounded-full" style={{ left: "0%", right: "100%" }}></div>
                                <Slider.Root
                                  className="relative flex w-full touch-none select-none flex-col items-center flex-1 self-center mx-2"
                                  value={[myBetAmount]}
                                  onValueChange={([value]: [number]) => changeBetAmount(value)}
                                  min={Number(formatTwoDecimalsExact(minBet))}
                                  max={Number(formatTwoDecimalsExact(maxBet))}
                                  step={0.01}
                                  aria-label="Slider"
                                >
                                  <Slider.Track className="relative h-2.5 w-full grow rounded-full light-darkness">
                                    <Slider.Range className="absolute h-full bg-linear-to-r from-brand to-brand_alt rounded-full" />
                                  </Slider.Track>
                                  <Slider.Thumb
                                    className="block w-4.5 h-6 rounded-lg transition-colors focus-visible:outline-none disabled:pointer-events-none disabled:opacity-40 relative cursor-pointer bg-alw_white -top-2"
                                  />
                                </Slider.Root>
                              </div>
                            </div>
                            <button
                              className="button focus-visible:outline-none h-10"
                              type="button"
                              onClick={() => changeBetAmount(maxBet)}
                            >
                              Max
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div id="auto-cashout-input" className="w-full @4xl:w-1/2">
                <div className="relative">
                  <div role="group" id="NumberField-cl-72">
                    <label id="NumberField-cl-72-label" className="font-semibold peer-disabled:cursor-not-allowed peer-disabled:opacity-40 text-secondary data-invalid:text-secondary px-1 flex w-full items-center justify-between mb-1 text-sm">
                      <span className="font-extrabold">
                        Auto cash-out
                      </span>
                      {/* <span>Chance 0.99%</span> */}
                    </label>
                    <div className="relative font-extrabold">
                      <div className="input rounded-lg">
                        {fToBet || fBetted ? (
                          <input type="number" value={cashOutTarget} readOnly />
												) : (
													<input 
                            type="number"
                            inputMode="decimal"
														value={cashOutTarget}
														onChange={(e) => {
                              const attrs = state;
                              // eslint-disable-next-line react-hooks/immutability
                              attrs.userInfo[index]["target"] = Number(e.target.value);
                              update(attrs);
                            }}
														onBlur={(e) => onChangeBlur(Number(e.target.value) || 0, "cashOutAt")}
													/>
												)}
                      </div>
                      <div className="absolute right-1 top-1/2 -translate-y-1/2 flex items-center gap-1">
                        <b className="text-primary mr-1 text-base">×</b>
                        <div tabIndex={-1} className="bottom-1 right-1.5 inline-flex items-center justify-center text-secondary hover:opacity-100 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed static size-auto opacity-100" role="button">
                          <button
                            className="button button-input text-primary h-10 sm:h-8 w-12.5 rounded-md"
                            type="button"
                            onClick={() => onChangeBlur(cashOutTarget - 1, "cashOutAt")}
                          >
                            <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none">
                              <path stroke="currentColor" strokeWidth="2.4" d="M18.4 11.2 13.6 16l4.8 4.8"></path>
                            </svg>
                          </button>
                        </div>
                        <div tabIndex={-1} className="right-1.5 top-1 inline-flex items-center justify-center text-secondary hover:opacity-100 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed static size-auto opacity-100" role="button">
                          <button
                            className="button button-input text-primary h-10 sm:h-8 w-12.5 rounded-md"
                            type="button"
                            onClick={() => onChangeBlur(cashOutTarget + 1, "cashOutAt")}
                          >
                            <svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" className="rotate-180">
                              <path stroke="currentColor" strokeWidth="2.4" d="M18.4 11.2 13.6 16l4.8 4.8"></path>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div id="bet-button" className="mt-1.5">
                <div className="relative w-full flex items-center justify-center">
                  <div className="w-full md:w-1/2">
                  {fBetted ? (
                    gameState === "RUNNING" ? (
                      <button
                        id="cash-out-button"
                        className="button flex-1 w-full max-w-100 flex-row items-center gap-2 justify-center text-primary_brand md:h-12 mx-auto"
                        type="button"
                        style={{
                          background: "linear-gradient(270deg, rgb(252, 224, 131) 0%, rgb(242, 171, 90) 100%)",
                          boxShadow: "rgba(241, 214, 65, 0.3) 0px 0px 12px 0px, rgb(226, 146, 54) 0px -2px 0px 0px inset"
                        }}
                        onClick={() => { callCashOut(index) }}
                      >
                        <div className="grow w-1/2 text-right">Cash Out</div>
                        {/* <div className="rounded-full inline-flex shrink-0 size-6 items-center justify-center leading-6">
                          <img src="/USD.png" className="h-3 w-4 border-[0.005rem]" />
                        </div> */}
                        <div className="text-left w-1/2 font-mono">
                          ${formatTwoDecimalsExact(betAmount * currentTarget)}
                        </div>
                      </button>
                    ) : (
                      <button id="loading-button" className="button button-brand flex-1 w-full md:max-w-100 text-black md:mx-auto md:h-12" type="button" disabled={true}>
                        Loading...
                      </button>
                    )
                  ) : (
                    fToBet ? (
                      <button
                        id="cancel-button"
                        className="button button-brand-red flex-1 w-full m-auto text-primary_brand font-extrabold md:max-w-100 md:h-12 bg-secondary!"
                        type="button"
                        onClick={() => {
                          onBetClick(false);
                          update({ ...state, [`${index}autoCound`]: 0, userInfo: { ...state.userInfo, [index]: { ...state.userInfo[index], auto: false } } })
                        }}
                      >
                        <span className="flex flex-row gap-1 items-center justify-center leading-tight">
                          <span>Loading...</span>
                          <span>(Cancel)</span>
                        </span>
                      </button>
                    ) : (
                      <button
                        id="bet-button-inner"
                        className="button button-brand flex-1 w-full m-auto text-primary_brand font-extrabold md:max-w-100 md:h-12"
                        type="button"
                        onClick={() => {
                          if (betAmount <= minBet ) {
                            //
                          }
                          else if (betAmount > maxBet) {
                            setShowPopOverLay(true);
                          } else {
                            onBetClick(true);
                          }
                        }}
                      >
                        <span className="flex flex-row gap-1 items-center justify-center leading-tight">
                          <span>Bet</span>
                          { gameState === 'RUNNING' && <span>(Next Round)</span> }
                        </span>
                      </button> 
                    )
                  )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BetControls;
