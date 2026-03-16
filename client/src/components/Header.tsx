import { useMemo, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

import {
  initDataState as _initDataState,
  type User,
  useSignal,
} from '@telegram-apps/sdk-react';

import { useMainContext } from "../context/mainContext";
import { formatTwoDecimalsExact } from '../utils/formatters';


export const Header = () => {
  const navigate = useNavigate();

  const initDataState = useSignal(_initDataState);
  const { state, fBetted } = useMainContext();

  const iconRef = useRef<SVGSVGElement | null>(null);
  const rotation = useRef(0);

  const user = useMemo<User | undefined>(() => {
    return initDataState?.user
  }, [initDataState]);

  const rotate = () => {
    rotation.current += 360; // always rotate clockwise
    iconRef.current?.style.setProperty(
      "transform",
      `rotate(${rotation.current}deg)`
    );
  }

  const reloadBalance = async () => {
    rotate();
    // ...
  };

  return (
    <div className="dialog-title">
      {/* <button className="button dialog-back" type="button">
        <svg className="icon" viewBox="0 0 32 32"></svg>
      </button> */}
      <div className="center right-auto left-4 absolute">
        <div className="flex h-10 rounded-xl relative w-52 border-2 p-0.5 sm:w-66 border-white_alpha5 bg-white_alpha10">
          <div className="mr-1 flex cursor-pointer select-none items-center ml-1.5 flex-auto">
            {/* <img className="mr-1.5 flex h-3 w-4 flex-none border-[0.005rem]" src="/USD.png" /> */}
            <div className="font-extrabold flex items-center w-0 flex-auto truncate">
                $&nbsp;{formatTwoDecimalsExact(state.userInfo.balance)}
            </div>
            {/* <svg className="icon -rotate-90 text-secondary w-4" viewBox="0 0 32 32"></svg> */}
          </div>
          <div className="flex items-center cursor-pointer select-none">
            {!fBetted && (
              <button
                id="reload"
                className="button ml-auto h-8 flex-none"
                type="button"
                onClick={reloadBalance}
              >
                <svg
                  ref={iconRef}
                  className="icon size-5 text-gray-300 transform transition-transform duration-500 rotate-0"
                  viewBox="0 0 32 32"
                >
                  <path d="M26.667 8H22.667C21.93 8 21.333 8.597 21.333 9.333C21.333 10.07 21.93 10.667 22.667 10.667H24.549C23.06 8.6 20.668 7.333 18 7.333C13.398 7.333 9.66699 11.065 9.66699 15.667C9.66699 20.269 13.398 24 18 24C20.573 24 22.933 22.814 24.421 20.855C24.862 20.28 24.745 19.453 24.171 19.012C23.596 18.571 22.769 18.688 22.328 19.262C21.199 20.705 19.657 21.556 18 21.556C15.054 21.556 12.777 19.279 12.777 16.333C12.777 13.388 15.054 11.111 18 11.111C19.495 11.111 20.872 11.802 21.773 12.963L19.333 15.333C18.844 15.833 19.212 16.667 19.904 16.667H26.667C27.403 16.667 28 16.07 28 15.333V8.667C28 7.93 27.403 7.333 26.667 8Z"/>
                </svg>
              </button>
            )}
            <button
              className="button button-brand ml-auto h-8 flex-none rounded-lg"
              type="button"
              onClick={() => navigate("/deposit")}
            >
              <svg className="icon size-4" viewBox="0 0 32 32"><path d="M17.0001 4.37061C15.8647 4.37061 14.9443 5.29101 14.9443 6.42638L14.9443 13.944H7.42668C6.2913 13.944 5.3709 14.8644 5.3709 15.9998C5.3709 17.1352 6.2913 18.0556 7.42667 18.0556H14.9441V25.5736C14.9441 26.709 15.8645 27.6294 16.9999 27.6294C18.1353 27.6294 19.0557 26.709 19.0557 25.5736V18.0559L26.5733 18.0559C27.7087 18.0559 28.6291 17.1355 28.6291 16.0002C28.6291 14.8648 27.7087 13.9444 26.5733 13.9444L19.0559 13.9444L19.0559 6.42638C19.0559 5.291 18.1355 4.37061 17.0001 4.37061Z"></path></svg>
            </button>
          </div>
        </div>
      </div>
      <button
        className="h-[90%] aspect-square p-1 rounded-full bg-layer5 ml-auto mr-4"
        onClick={() => navigate('/profile')}
      >
        <div className="w-full h-full rounded-full center">
          <img alt="avatar" className="w-full h-full rounded-full" src={user?.photo_url} />
        </div>
      </button>
      <div className="ml-auto absolute right-4 top-0 flex items-center h-full"></div>
    </div>
  )
}

export default Header;
