Integration test suite for cloudstack.

Somewhat inspired by existing cloudstack smoke test suite that uses marvin, but written

* without data dependencies or large/static fixtures (no test needs deployDataCenter)
* as lots of tiny unit-test-style test methods as much as possible, rather than as large scenario tests
* to be re-runnable multiple times against a running server without cleaning it out
* to use randomized data
* without dependency on nosetests (or any other framework) so easy to use from any IDE
* for easy readability, including PEP8-compliance and object orientation
* including error and error recovery scenarios

Currently uses the marvin api client, wrapping it with a strongly typed pythonic object model.

Requirements
------------
* cloudstack management server accessible at http://localhost:8080/client/ or set environment variables:
** CS_HOST, CS_PORT, CS_USER, CS_PROTOCOL or CS_BASE_URL
** CS_PASSWORD or CS_API_KEY and CS_SECRET_KEY
* marvin install matching the running management server
* 'python' command invokes python2.7 or later

Running tests
-------------
* `export DEBUG=1` to enable debug logging
* `export TRACE=1` to enable request tracing
* all tests: `./test.sh`
* specific directory: `./test.sh -s dir`
* specific test pattern: `./test.sh -p pattern`
* single file `PYTHONPATH=\`pwd\` python path/to/test_suite.py`
* or use py.test, nosetest, PyDev, PyCharm, or anything else

Adding tests
------------
* just write python unit test any way you want
* subclass cstest.framework.CITTestCase to get a hold of API clients, for example

```python

from cstest.framework import CITTestCase
from csapi.apiclient import CloudstackAPIException

class ExampleTestCase(CITTestCase):
    @classmethod
    def setUpClass(cls):
        super(UserTestCase, cls).setUpClass()

    def test_hello(self):
        user = self.data.random_user()
        self.user_api.create(user)


if __name__ == '__main__':
    from unittest import main
    main()
```

Expanding API support
---------------------
These tests use a 'strongly' typed API (insofar as that is possible with python), providing type annotations that can be recognized by PyCharm. These APIs are defined in the `csapi` package. 

While intended to be mostly auto-generate-able later on, right now these files are made manually by munging the marvin cloudstackAPI code and copy/paste.

After adding an API, please also

* add a random data generator to `cstest/random_data.py`
* add an api instance to `cstest/framework.py`
* add at least basic CRUD converage for that API

Plans
-----
Provided we find sufficient time to do it, tasks include

...expand on this new suite to have better coverage than the smoke test suite, and replace the cloudstack smoke tests.

...remove usage of marvin and fully auto-generate custom API.

...split of API into properly independent library.

...rewrite libcloud on top of that library.

...rewrite cloudstack integration component test suite to follow same/similar pattern.
