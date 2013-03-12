======
Funnel
======

Capturing output to a list
--------------------------

Funnel lets you capture the stdout and stderr of a Python script into a simple list for later processing.

Take, for example, this ``demo_output.py`` script::

    #!/usr/bin/env python

    import os
    import sys

    print("Hello!")
    sys.stderr.write('Multi-line{0}Error!{0}'.format(os.linesep))

It could have its output captured and validated like so::

    #!/usr/bin/env python

    import funnel

    with funnel.capture_output() as out:
        execfile('demo_output.py')

    result = out.get_output()

    assert result == [
        ('stdout', 'Hello!'),
        ('stderr', 'Multi-line'),
        ('stderr', 'Error!')]

The resultant list is very human-readable; each line gets its own entry in the list and notes its source.


Redirecting output to a file
----------------------------

Funnel can also write the combined and labeled output to a file::

    #!/usr/bin/env python

    import funnel

    with funnel.redirect_output_to_file('demo_output.log'):
        execfile('demo_output.py')

The above would result in the file ``demo_output.log`` containing the following lines::

    [stdout] Hello!
    [stderr] Multi-line
    [stderr] Error!


Funnel handles interlaced line fragments
----------------------------------------

Imagine, if you will, the following scenario::

    #!/usr/bin/env python

    import os
    import sys

    def load_file():
        sys.stderr.write("ERROR: I should raise an error, but I'm badly written!" + os.linesep)

    sys.stdout.write('Loading file...')
    load_file()
    sys.stdout.write('done' + os.linesep)

Normally, you'd expect to see the following output in the console::

    Loading file...ERROR: I should raise an error, but I'm badly written!
    done

With funnel, the output looks a bit nicer::

    [stderr] ERROR: I should raise an error, but I'm badly written!
    [stdout] Loading file...done

The "Loading file" line is appended to the output when the line is completed. If the line is never completed, it is written out when funnel is cleaned-up.
