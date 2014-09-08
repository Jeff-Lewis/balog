balog
=====

Balanced event logging schema and library

Log schema design goals
=======================

 - Schema version annotated
 - Provide sufficient information about the event
 - Open and close (be flexible, avoid unnecessary change to schema)

Design rationals
================

OSI Network Model Structure
---------------------------

Data in the log can be divided into two major groups, one is the meta data,
which is the data about the event. The another group is the log for application 
itself. In most cases, applications should only be interested in the 
application log itself. And the logging facility should only be interested in 
how to handle the whole event rather than to consume the content of application 
log. Also, since schema of application can variant, we don't want change the
whole schema everytime when application log is change. Consider these issues,
one idea come to my mind is Internet OSI model is actually dealing with the
same issue. It's like TCP/IP protocol doesn't need to know the content of
application layer. Similarly, logging facility doesn't have to know the content
of application log. With this idea in mind, I define two layers for our logging
system.

 - Facility layer
 - Application layer

Facility layer is all about the event, when it is generated, who emited this
event, what's its routing tag and etc. Application layer is all about
application data, like a dispute is processed, a debit is created and etc.

Facility layer
==============

Header
------

id (required)
~~~~~~~~~~~~~

The unique GUID for this event, starts with `LG` prefix.

channel (required)
~~~~~~~~~~~~~~~~~~

The tag for routing event, e.g. `justitia.models.disputes.created`.

timestamp (required)
~~~~~~~~~~~~~~~~~~~~

Creating time for this event, should be in ISO8601 format with UTC timezone.

schema (required)
~~~~~~~~~~~~~~~~~

The integer number indicates the version of schema.

payload (required)
~~~~~~~~~~~~~~~~~~

Payload of this log.

open_content (optional)
~~~~~~~~~~~~~~~~~~~~~~~

Open content of this log.

source (optional)
~~~~~~~~~~~~~~~~~

Source of this event, usually a FQDN of host. Since this might not given by
application when the event is generated, it could be attached by fluented
or other log processor, so it should be optional.

composition (optional)
~~~~~~~~~~~~~~~~~~~~~~

Is this event a composited event. If this field is not present, then composition
value is default to `false`.

TODO

Payload
-------

TODO

Open content
------------

TODO
