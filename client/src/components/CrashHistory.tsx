import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from "../utils/formatters";


const CrashHistory = () => {
  const { state, showCrashHistory, setShowCrashHistory, getColorClasses } = useMainContext();

  return (
    <div>
      <div id="crash-history" className="px-2 flex">
        <div className="relative overflow-hidden flex-auto bg-layer5 h-8 rounded-lg md:h-10 pr-8 sm:pr-10" style={{ width: 'calc(100% - 3rem)' }}>
          <div className="grid grid-flow-col gap-1 h-full overflow-x-visible -translate-x-[19.1667%] grid-cols-[repeat(6,calc(20%-0.3rem))]">
            {[...state.gameHistory].slice(0, 6).reverse().map((game, index) => {
              const { bg, text } = getColorClasses(game.crashPoint);
              return (
                <div key={index} className="flex items-center justify-center gap-1 px-2 h-full cursor-pointer">
                  <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${bg}`}></span>
                  <span className="flex flex-col">
                    <span className={`text-xs sm:text-sm leading-tight text-left whitespace-nowrap font-extrabold ${text}`}>
                      {formatTwoDecimalsExact(game.crashPoint)}x
                    </span>
                  </span>
                </div>
              );
            })}
          </div>
          <div
            className="w-9 sm:w-11 h-6 sm:h-8 absolute right-0 top-1 bg-layer5"
            onClick={ () => setShowCrashHistory(!showCrashHistory) }
          >
            <div className="w-8 h-6 sm:w-10 sm:h-8 flex justify-center items-center bg-layer6 mr-1 rounded-md cursor-pointer">
              <svg width="15" height="16" viewBox="0 0 15 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M7.5 0.5C11.6421 0.5 15 3.85786 15 8C15 12.1421 11.6421 15.5 7.5 15.5C3.35786 15.5 0 12.1421 0 8C0 3.85786 3.35786 0.5 7.5 0.5ZM7.5 2.10714C4.24554 2.10714 1.60714 4.74554 1.60714 8C1.60714 11.2545 4.24554 13.8929 7.5 13.8929C10.7545 13.8929 13.3929 11.2545 13.3929 8C13.3929 4.74554 10.7545 2.10714 7.5 2.10714ZM6.96429 3.785C7.45607 3.785 7.85946 4.16375 7.89857 4.64536L7.90179 4.7225V8.28982L10.4689 8.29036C10.9864 8.29036 11.4064 8.71036 11.4064 9.22786C11.4064 9.71964 11.0277 10.123 10.5461 10.1621L10.4689 10.1654H6.96429C6.89036 10.1654 6.81804 10.1568 6.74893 10.1407C6.74518 10.1396 6.74143 10.1391 6.73768 10.138C6.72429 10.1348 6.71089 10.1311 6.69804 10.1273C6.68518 10.1236 6.67071 10.1187 6.65732 10.1145C6.65143 10.1123 6.64554 10.1102 6.63964 10.108C6.6225 10.1016 6.60536 10.0946 6.58875 10.0877C6.57804 10.0829 6.56839 10.0786 6.55821 10.0737C6.5475 10.0684 6.53625 10.063 6.52554 10.0571C6.51214 10.0502 6.49875 10.0427 6.48536 10.0346C6.47679 10.0298 6.46875 10.0245 6.46018 10.0191C6.45054 10.0132 6.44143 10.0068 6.43232 10.0004C6.41946 9.99125 6.40661 9.98214 6.39429 9.9725C6.38625 9.96661 6.37821 9.96018 6.37018 9.95375C6.36 9.94571 6.35089 9.93768 6.34125 9.92911C6.33161 9.92054 6.32304 9.9125 6.31446 9.90393C6.30536 9.89536 6.29679 9.88679 6.28875 9.87821C6.27857 9.86804 6.26893 9.85732 6.25929 9.84607C6.25339 9.83911 6.2475 9.83214 6.24161 9.82518C6.23304 9.815 6.225 9.80482 6.21696 9.79411C6.20839 9.78286 6.20036 9.77161 6.19179 9.75982C6.18536 9.75071 6.17946 9.74107 6.17304 9.73196C6.16661 9.72179 6.16018 9.71107 6.15375 9.70089C6.14732 9.69071 6.14143 9.67893 6.13554 9.66768C6.12911 9.65589 6.12321 9.64357 6.11732 9.63125C6.1125 9.62054 6.10768 9.61036 6.10286 9.59964C6.09857 9.58946 6.09429 9.57982 6.09054 9.56964C6.07661 9.53375 6.06482 9.49679 6.05518 9.45929C6.03643 9.38536 6.02679 9.30821 6.02679 9.22839V4.72304C6.02679 4.20554 6.44679 3.78554 6.96429 3.78554V3.785Z"
                  fill="#B3BEC1"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CrashHistory;
