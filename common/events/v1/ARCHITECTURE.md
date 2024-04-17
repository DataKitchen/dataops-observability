# Event Dataclasses

This document describes the high-level architecture and concepts of the Events

## Purpose

In the application, "Events" are essentially at the core of the entire system.  Every part of the system either consumes an Event
or creates one from incoming data (or both).  As such, there needs to be a single centralized Event class set for all pieces
of the application to use so that they are all basically "speaking the same language".

## Event Structure

All Events are defined as children to `Event`, which itself also includes "metadata" for an event, along with specific
identifying information.  The `Event` also defines extendable (de)serialization methods for all child classes.  The
intention with this is to have Events know how to (de)serialize themselves so that there's no need to write custom code for
each module in the application that consumes/produces the events.  (De)serialization also supports translation to/from both
JSON (`dict`) and `bytes` so that the Events can be consumed by the various modules that need them.

**NOTE**: _Please think long and hard about adding any additional logic to the (de)serialization methods, as this can potentially
have far-reaching effects.  Ideally any nitpicky logic for an event type should be handled by the `marshmallow` schema
or a function on the `Event` subclass being acted upon._

Each Event also defines a "Schema" using `marshmallow` that is used for two purposes:

1. During deserialization the schema provides validation on the Event for free as it happens
2. The API(s) that use Events can use this information to define request/response bodies for the Event objects.

## Usage

As stated earlier, the goal of these Events is to provide them as a central datastructure for all modules to use in the
application.  If a module either consumes or produces Events (as they are understood by the system), that module's interface
should be accepting Event objects, and returning Event objects.  Any (de)serialization or transforms that need to happen
to the Event that are specific to the module should be handled internally to the module itself, so that logic specific to
one module doesn't leak into the shared pieces of the Event objects.

_i.e. We don't want to see methods like `do_stuff_for_rules_engine()`
on the `Event`.  If the Rules Engine needs special logic, it should handle that internally since no other module cares
about that function_

## Organization & Creation

Creating a new Event type should be a relatively straightforward process as long as the desired contents of the Event are known:

- Create a new `@dataclass` that inherits from `Event`
- Add any new fields that are needed for the new Event type
- In the same file as the dataclass, create a new Schema that inherits from `EventSchema`
  - Utilize the `marshmallow` fields and validation params to make the schema robust and easy to validate
- Add `__schema__ = MyNewSchema` to the new Event dataclass to link the two for deserialization.
  - _If this line is not added, it will throw an `AttributeError`_
- Add an import to the `events/__init__.py` for the new event file

## Nested Data in Events

If there is a need to do nested dataclasses for the Event, there is a recommended way to handle this:

- The schema for the nested data should inherit from **`Schema`**, NOT from `EventSchema`
- Add a `@post_load` function for unpacking the data into the correct nested dataclass (should be a one-liner)

If these 2 simple steps are followed, it should seamlessly allow deserialization to unpack nested data.
This should work nesting infinitely down too; was tested with 3 nested classes and worked fine.

Please take a look at `TestOutcomeEvent` as a good example, and mimic what it does to enable nice and clean
nested deserialization.

## Common Errors

- If there is a need make a nested dataclass and from_dict() fails with something like
`TypeError: __init__() missing 1 required positional argument: 'foo'`, That usually means that the Marshmallow schema
- was not created correctly, and are likely either missing setting `load_default=None` (for "Optional" properties
on the dataclass) or setting `required=True`
