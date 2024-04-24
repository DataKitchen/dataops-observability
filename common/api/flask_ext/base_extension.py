__all__ = ["BaseExtension"]
from typing import Optional

from flask import Flask
from flask.typing import AfterRequestCallable, AppOrBlueprintKey, BeforeRequestCallable


class BaseExtension:
    def __init__(self, app: Optional[Flask] = None) -> None:
        if app is not None:
            self.app = app
            self.init_app()

    def add_before_request_func(self, func: BeforeRequestCallable, key: AppOrBlueprintKey = None) -> None:
        """
        Helper for adding new @before_request callback functions, so that multiple
        independent extensions can add their own without overriding each other.

        This is designed to append to the list, so that @before_request functions from
        multiple extensions will run in the order the extensions were declared.
        """
        self.app.before_request_funcs.setdefault(key, []).append(func)

    def add_or_move_before_request_func(self, func: BeforeRequestCallable, key: AppOrBlueprintKey = None) -> None:
        """
        Appends the function if it doesn't exist, if it does, moves it to the end of the function stack.

        If the given function doesn't exist then it is appended like normal. If the value is already present, it is
        removed from its current position in the list and appended to the end.

        This is useful when more than one plugin may attempt to add the same before request function to the stack. The
        plugin that adds it last will be the one which dictates where in the stack the value should go.
        """
        before_funcs = self.app.before_request_funcs.setdefault(key, [])
        try:
            func_idx = before_funcs.index(func)
        except ValueError:
            # This function wasn't in the list so just append it to the end
            before_funcs.append(func)
        else:
            # Pop from the current index and append to the end of the function list
            before_funcs.append(before_funcs.pop(func_idx))

    def add_after_request_func(self, func: AfterRequestCallable, key: AppOrBlueprintKey = None) -> None:
        """
        Helper for adding new @after_request callback functions, so that multiple
        independent extensions can add their own without overriding each other.

        This is designed to append to the list, so that @after_request functions from
        multiple extensions will run in the order the extensions were declared.
        """
        self.app.after_request_funcs.setdefault(key, []).append(func)

    def init_app(self) -> None:
        raise NotImplementedError
