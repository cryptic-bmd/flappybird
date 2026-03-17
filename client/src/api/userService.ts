import axios from 'axios';
import { API_URL } from "../config";

export interface UserInfo {
  id: number;
  balance: number;
  availableBalance: number;
  referralLink: string;
}

const fetchUserInfo = async (token: string): Promise<UserInfo> => {
  const response = await axios.get(
    `${API_URL}/user/info`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  if (response.status === 200) {
    // log(`response.data: ${response.data}`);
    return response.data;
  } else {
    throw new Error('Unable to fetch user info');
  }
}

export default fetchUserInfo;
