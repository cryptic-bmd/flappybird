import { useState, useEffect } from 'react';
import axios from 'axios';

import Dialog from '../components/Dialog.tsx';
import { Page } from '../components/Page.tsx';
import { API_URL } from '../config.ts';
import { useAuthContext } from '../context/authContext.ts';
import { getAxiosError } from '../utils/errors.ts';
import { formatTwoDecimalsExact } from '../utils/formatters.ts';
import { log } from '../utils/logger.ts';

const Status = {
  Pending: "Pending",
  Completed: "Completed",
  Failed: "Failed",
  Cancelled : "Cancelled",
} as const;
type Status = typeof Status[keyof typeof Status];

interface Referral {
  referredId: number;
  referredName: string;
  bonusAmount: number;
  status: Status;
  createdAt: string;
}


const Referral: React.FC = () => {
  const { token, setError } = useAuthContext();

  const [loading, setLoading] = useState(false);
  const [referrals, setReferrals] = useState<Referral[]>([]);

  useEffect(() => {
    const fetchReferrals = async () => {
      setLoading(true);
      // setReferrals([]);

      if (!token) {
        log('No token');
        return;
      }
      try {
        const response = await axios.get<Referral[]>(
          `${API_URL}/referral/history`,
          { headers: { Authorization: `Bearer ${token}` } }
        );
        if (response.status === 200) {
          log(response.data)
          setReferrals(response.data);
        } else {
          log(`Error getting deposit details`);
          setError({ message: "Unable to deposit details" });
        }
      } catch(e) {
        setError({ message: getAxiosError(e), autoClose: 5000 });
      }

      setLoading(false);
    };
  
    fetchReferrals();
  }, [token, setError]);

  return (
    <Page>
      <Dialog>
        <div className="dialog-item">
          <div className="dialog-title">
            Referrals
            <div className="ml-auto absolute right-4 top-0 flex items-center h-full"></div>
          </div>
          <div className="scroll-y dialog-content">
            <div className="scroll-container">
              <div className="sm:mx-0 rounded-xl flex-auto bg-layer2">
                <div className="flex flex-none justify-between rounded-xl px-4 py-3 mt-3 bg-layer3">
                  <div className="flex-1">Name/ID</div>
                  <div className="flex-1 text-right">Amount/Status</div>
                </div>
                <div className="grid grid-cols-1">
                  {!loading ? (
                    <>
                      {referrals.length === 0 && (
                        <section className="py-10 text-center center flex-col col-span-full">
                          <img className="w-48 h-48" src="/chihuahua.png" />
                          <div className="leading-5 mt-4">Oops! There is no data yet!</div>
                        </section>
                      )}
                      <div className="grid grid-cols-1">
                        {referrals.map((referral, index) => (
                          <div key={index} className="border-b border-third">
                            <div
                              className="flex items-center justify-between flex-none" // cursor-pointer border-third hover:rounded-sm hover:bg-black_alpha5 dark:hover:bg-white_alpha5 inactive"
                            >
                              <div className="flex flex-1 p-4 text-base font-extrabold ellipsis flex-col items-start">
                                <div>{referral.referredName}</div>
                                <div className="text-secondary text-[12px]">{(new Date(referral.createdAt)).toLocaleString()}</div>
                              </div>
                              <div className="flex flex-1 p-4 text-base font-bold ellipsis flex-col items-end">
                                <div className={`flex items-center ${referral.status === Status.Completed ? "text-success" : ""} text-base justify-end sm:justify-center`}>
                                  {referral.status === Status.Completed && (
                                    <>{formatTwoDecimalsExact(referral.bonusAmount)}&nbsp;<span>USDT</span></>
                                  )}
                                </div>
                                <div className="flex items-center text-secondary justify-end sm:hidden">
                                  <svg fill="currentColor" className={`size-4 ${referral.status === Status.Completed ? "text-success" : "text-warning"}`} viewBox="0 0 32 32">
                                    <path d="M16 8 a8 8 0 1 0 0.0001 0"></path>
                                  </svg>
                                  <div className="ml-1">{referral.status}</div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {referrals.length > 0 && <div className="col-span-full h-20 font-extrabold center">No More</div>}
                    </>
                  ) : (
                    <div className="py-10 text-center center flex-col col-span-full">
                      <div className="leading-5 mt-4">Loading...</div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </Dialog>
    </Page>
  )
}

export default Referral;
