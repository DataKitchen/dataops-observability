# type: ignore
from invoke import Collection

from scripts.invocations import deploy, dev
from scripts.invocations.test import test_ns

"""
This is the top-level config for the `make`-like tool `invoke`.

The tasks are found in scripts/invocations where also any new task should be implemented. When suitable, create a new
module for the tasks. `invoke` has the concept of task collections as well as subcollections. Subcollections are
prependended to the final task name. i.e. `invoke test.unit` which can be helpful to avoid name collisions with
other invoke tasks.

Examples:

Run only tests marked as unittests
```
$ invoke test.unit
```

# Run some deploy task
```
$ invoke deploy.local
```

"""


namespace = Collection(deploy)
namespace.add_collection(dev)
namespace.add_collection(test_ns)
