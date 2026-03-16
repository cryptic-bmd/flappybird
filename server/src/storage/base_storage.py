import copy
from typing import Optional


class StateStorageBase:
    def __init__(self) -> None:
        pass

    def _get_key(
        self,
        prefix: str = "game",
        separator: str = ":",
        user_id: Optional[int] = None,
    ) -> str:
        """
        Convert parameters to a key.
        """

        params = [prefix]
        if user_id:
            params.append(str(user_id))

        return separator.join(params)

    def get_data(self, user_id: Optional[int] = None):
        """
        Get data for a user in a particular chat.
        """
        raise NotImplementedError

    def set_data(
        self,
        key,
        value,
        user_id: Optional[int] = None,
    ):
        """
        Set data for a user in a particular chat.
        """
        raise NotImplementedError

    def reset_data(
        self,
        user_id: Optional[int] = None,
    ):
        """
        Reset data for a particular user in a chat.
        """
        raise NotImplementedError

    def get_state(
        self,
        user_id: Optional[int] = None,
    ):
        raise NotImplementedError

    def set_state(
        self,
        state,
        user_id: Optional[int] = None,
    ):
        """
        Set state for a particular user.

        ! Note that you should create a
        record if it does not exist, and
        if a record with state already exists,
        you need to update a record.
        """
        raise NotImplementedError

    def delete_state(
        self,
        user_id: Optional[int] = None,
    ):
        """
        Delete state for a particular user.
        """
        raise NotImplementedError

    def get_interactive_data(
        self,
        user_id: Optional[int] = None,
    ):
        raise NotImplementedError

    def save(
        self,
        data,
        user_id: Optional[int] = None,
    ):
        raise NotImplementedError


class StateDataContext:
    """
    Class for data.
    """

    def __init__(
        self,
        obj: StateStorageBase,
        user_id: Optional[int] = None,
    ):
        self.obj = obj
        res = obj.get_data(user_id=user_id)
        self.data = copy.deepcopy(res)
        self.user_id = user_id

    def __enter__(self):
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.obj.save(
            self.user_id,
            self.data,
        )
