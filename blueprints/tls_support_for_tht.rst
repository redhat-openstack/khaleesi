..
 This work is licensed under a Creative Commons Attribution 3.0 Unported
 License.

 http://creativecommons.org/licenses/by/3.0/legalcode

==========================================
Add tls support for Tripleo Heat Templates
==========================================

In order for us to have a ssl installation of openstack we need some configuration templates files in place.

I'm proposing a python library file to extract the templates from tht and export the filled up files were we can use to create the overcloud

Problem description
===================

The problem is two fold and arises that the specific templates are versioned on tht, storing them on khaleesi 
(keeping two versions on different projects of the same file) just creates technical debt. 


The second part of the problem is that the templates themselves are not good for sed-ing in the parameters
that we need due that we have to add the certificate and key pems into a yaml

This is a snip of the template::

    parameter_defaults:
      SSLKey: |
        The contents of the private key go here
      ...

We need it filled like this::

    parameter_defaults:
      SSLKey: |
        -----BEGIN PRIVATE KEY-----
        MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC3TWYoCCDKdgFA
        0q4/OcbB3N15h8lWtM3BI2KzqOMa4sUhVcPvT5Sp7c0hNPu7yDwfRVBFCr+eyEIC
        o+1pSffmnp8Gzo4VeDWFcRjFymWXTw/fi8j1lj8jMZGH6lkqpgLDd1koUIxXpOKm
        HCkz2rdEdYpjjmGkNCUnAe3xlwolJAFXwg1GyPXPxAJ/r6Ylp+/9COxR7OCpbPGr
        lrN2q1rvntI4SrTfo+lX3lIlqvKbCnko7AECpGocC6+uV3au1T3OBwFAPh0u8OA3
        nJHKYkb8PAPpNRiUp1KX4o/9Y+zdm8uN/AIxcm7JtzFf8jIISjYMD4i0E6JrjYzw
        nVAQVmbNAgMBAAECggEBAJ8sWP9+P2tQmbn+uU0yEMSb1L8KCO6ARwPmhHlauQvJ
        zEEsRt7zDjeZxr2FUuw37u2AtTmfIdLyN1AvpaP+lYTwTUwN5hgCsQdVtJtdLGb+
        QtxueG26sM0Q6D1MZW3BhzjR1NxLRfN9vUtdvPHIhcivASN+qo96sKB07nkSHb8t
        UVLVJORYqlwIHZP5q+U4QFHftCwpE6WvrR4CuSc0PmnBualb9I0BVeAteVecifQG
        CTooUPFfF9enYuQSjnGpuaVunNxpJB69TR3YHP5N8GUXXqIXmEtuuoSpLXKCP2Xc
        7lg+uH4+VpKT2tlZOmhJU1Kk6OKoLLvDMG0Zf0eAaoECgYEA7DuHs/to81sm8fps
        EHcDCl9YNzGuDbGQ2bi73ff7QWm9FyULsm1Vp1Eu3uvsQa3RRaC5oPrtRU58OcoD
        n/4MEUKTDxjGUfw1NOfYPHeCSQHqM82L6AwwOMRH4qRV33hR16NDy8vhm+YseRNK
        AQcMFflp/tBO8aUc6P2Ui69UftECgYEAxqQFfFRo4ItBiMT/7i2oiJ3u3YDq/C2w
        l1DX+g7BD2SKHWmtxJJ4IiczxCL73tDrhLwp3kpqnyd5+6gdhgHtC/sJjx+RoThl
        A5To5Fd+vCvtoJlexsXPEgnIkZFNqwstRUAaI0iTIdt/Nzymzpn/iYp0Qc0p9/vo
        Unlq791C/z0CgYAnSxueZ2IkoHPQ6huRfYpG7mcI/z15T6DNZjnxiO8FCWaHdAUH
        D8KgixNlxw5MOnJFx5841KQk1BI7tot10FcHg/BcIX3TY0UiYLIKFMLaC/R922G7
        HlPjDVr7quQRwLy0RpbfTjFfsiCRnxC/LQHooczsso9/CDzP0GYl+ervEQKBgATe
        JBxF3UQTZYm6eiMWD1k5tY7MB/YiEH/ExWYlUmnUJuZNnqqAhF0h5MzbppxxNjRM
        gCIoZLB9wSl/lymfhnWSs0tElMcEoMUTsxlVY4+s6+fRmlb4pfhlMPsQOn0Eixl1
        Vq6iqqhbvqRV4iiR8YcnU24BXxPqomjS/OHf5DJpAoGBAIIzvr9nR2W7ci3m55l0
        5/EjeChqpVUBKiy6PGWWqj6kfeGlKnDbCJL3DBu5agc46WlJG143I3SvbgtVBwhy
        MJVRj77Zqk7BnOjAczTTxP2N/Ga7ZsWzJj8AlKpxBUEB6chdj2BLL3y+/JcuOEjg
        8LMslpo4Fx5NBmNcdvie06tf
        -----END PRIVATE KEY-----
    ...

Proposed change
===============

A simple python library can get the templates from the tht installation read the templates 
as a yaml structure do the required changes and output the fully templated files to where we can call 
with the -e parameter to openstack overcloud deploy


Alternatives
------------

The alternative is storing those templates on khaleesi but I feel that just brings techinical debt.


Implementation
==============

I have a implementation here: https://review.gerrithub.io/#/c/259773/


Assignee(s)
-----------

Primary assignee:

Adriano Petrich <apetrich@redhat.com>


