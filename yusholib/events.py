"""
    Event system for python
"""

import typing as T
import functools

from collections import defaultdict


class HandlerNotFound(Exception):
    """Raised if a handler wasn't found"""

    def __init__(self, event: str, handler: T.Callable) -> None:
        super().__init__()
        self.event = event
        self.handler = handler

    def __str__(self) -> str:
        return "Handler {} wasn't found for event {}".format(self.handler, self.event)


class EventNotFound(Exception):
    """Raised if an event wasn't found"""

    def __init__(self, event: str) -> None:
        super().__init__()
        self.event = event

    def __str__(self) -> str:
        return "Event {} wasn't found".format(self.event)


class Observable:
    """Event system for python"""

    def __init__(self) -> None:
        self._events = defaultdict(list)  # type: T.DefaultDict[str, T.List[T.Callable]]

    def get_all_handlers(self) -> T.Dict[str, T.List[T.Callable]]:
        """Returns a dict with event names as keys and lists of
        registered handlers as values."""

        events = {}
        for event, handlers in self._events.items():
            events[event] = list(handlers)
        return events

    def get_handlers(self, event: str) -> T.List[T.Callable]:
        """Returns a list of handlers registered for the given event."""

        return list(self._events.get(event, []))

    def is_registered(self, event: str, handler: T.Callable) -> bool:
        """Returns whether the given handler is registered for the
        given event."""

        return handler in self._events.get(event, [])

    def on(  # pylint: disable=invalid-name
            self, event: str, *handlers: T.Callable
    ) -> T.Callable:
        """Registers one or more handlers to a specified event.
        This method may as well be used as a decorator for the handler."""

        def _on_wrapper(*handlers: T.Callable) -> T.Callable:
            """wrapper for on decorator"""
            self._events[event].extend(handlers)
            return handlers[0]

        if handlers:
            return _on_wrapper(*handlers)
        return _on_wrapper

    def off(  # pylint: disable=keyword-arg-before-vararg
            self, event: str = None, *handlers: T.Callable #type: ignore
    ) -> None:
        """Unregisters a whole event (if no handlers are given) or one
        or more handlers from an event.
        Raises EventNotFound when the given event isn't registered.
        Raises HandlerNotFound when a given handler isn't registered."""

        if not event:
            self._events.clear()
            return

        if event not in self._events:
            raise EventNotFound(event)

        if not handlers:
            self._events.pop(event)
            return

        for callback in handlers:
            if callback not in self._events[event]:
                raise HandlerNotFound(event, callback)
            while callback in self._events[event]:
                self._events[event].remove(callback)
        return

    def once(self, event: str, *handlers: T.Callable) -> T.Callable:
        """Registers one or more handlers to a specified event, but
        removes them when the event is first triggered.
        This method may as well be used as a decorator for the handler."""

        def _once_wrapper(*handlers: T.Callable) -> T.Callable:
            """Wrapper for 'once' decorator"""

            def _wrapper(*args: T.Any, **kw: T.Any) -> None:
                """Wrapper that unregisters itself before executing
                the handlers"""

                self.off(event, _wrapper)
                for handler in handlers:
                    handler(*args, **kw)

            return _wrapper

        if handlers:
            return self.on(event, _once_wrapper(*handlers))
        return lambda x: self.on(event, _once_wrapper(x))

    def trigger(self, event: str, *args: T.Any, **kw: T.Any) -> bool:
        """Triggers all handlers which are subscribed to an event.
        Returns True when there were callbacks to execute, False otherwise."""

        callbacks = list(self._events.get(event, []))
        if not callbacks:
            return False

        for callback in callbacks:
            callback(*args, **kw)
        return True

def _preserve_settings(method: T.Callable) -> T.Callable:
    """Decorator that ensures ObservableProperty-specific attributes
    are kept when using methods to change deleter, getter or setter."""

    @functools.wraps(method)
    def _wrapper(
            old: "ObservableProperty", handler: T.Callable
    ) -> "ObservableProperty":
        new = method(old, handler)  # type: ObservableProperty
        new.event = old.event
        new.observable = old.observable
        return new

    return _wrapper


class ObservableProperty(property):
    """
    A property that can be observed easily by listening for some special,
    auto-generated events.
    """

    def __init__(
            self, *args: T.Any,
            event: str = None, observable: T.Union[Observable, str] = None, # type: ignore
            **kwargs: T.Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.event = event
        self.observable = observable

    def __delete__(self, instance: T.Any) -> None:
        if self.fdel is not None:
            self._trigger_event(instance, self.fdel.__name__, "before_del")
        super().__delete__(instance)
        self._trigger_event(instance, self.fdel.__name__, "after_del") # type: ignore

    def __get__(self, instance: T.Any, owner: T.Any = None) -> T.Any:
        if instance is None:
            return super().__get__(instance, owner)
        if self.fget is not None:
            self._trigger_event(instance, self.fget.__name__, "before_get")
        value = super().__get__(instance, owner)
        if instance is None:
            return value
        self._trigger_event(instance, self.fget.__name__, "after_get", value) # type: ignore
        return value

    def __set__(self, instance: T.Any, value: T.Any) -> None:
        if self.fset is not None:
            self._trigger_event(instance, self.fset.__name__,
                                "before_set", value)
        super().__set__(instance, value)
        self._trigger_event(instance, self.fset.__name__, "after_set", value) # type: ignore

    def _trigger_event(
            self, holder: T.Any, alt_name: str, action: str, *event_args: T.Any
    ) -> None:
        """Triggers an event on the associated Observable object.
        The Holder is the object this property is a member of, alt_name
        is used as the event name when self.event is not set, action is
        prepended to the event name and event_args are passed through
        to the registered event handlers."""

        if isinstance(self.observable, Observable):
            observable = self.observable
        elif isinstance(self.observable, str):
            observable = getattr(holder, self.observable)
        elif isinstance(holder, Observable):
            observable = holder
        else:
            raise TypeError(
                "This ObservableProperty is no member of an Observable "
                "object. Specify where to find the Observable object for "
                "triggering events with the observable keyword argument "
                "when initializing the ObservableProperty."
            )

        name = alt_name if self.event is None else self.event
        event = "{}_{}".format(action, name)
        observable.trigger(event, *event_args)

    deleter = _preserve_settings(property.deleter)
    getter = _preserve_settings(property.getter)
    setter = _preserve_settings(property.setter)

    @classmethod
    def create_with(
            cls, event: str = None, observable: T.Union[str, Observable] = None # type: ignore
    ) -> T.Callable[..., "ObservableProperty"]:
        """Creates a partial application of ObservableProperty with
        event and observable preset."""

        return functools.partial(cls, event=event, observable=observable)