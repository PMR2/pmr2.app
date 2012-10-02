Introduction
============

This is the Physiome Model Repository 2 (PMR2) core library. 

PMR2 is a software system designed to provide management of models in a
user friendly way using a content management system (CMS), which
provides the management interface to the underlying model and associated
data, which are stored using a distributed version control system
(DVCS).  This CMS used depended on by PMR2 is Plone_, and currently
Mercurial_ is the only DVCS supported through the extension package
pmr2.mercurial_.

.. _Plone: http://plone.org/
.. _Mercurial: http://mercurial.selenic.com/
.. _pmr2.mercurial: https://github.com/PMR2/pmr2.mercurial/

PMR2 is constructed in a way where it is extensible, thus
additional storage method can be implemented alongside Mercurial along
with the presentation views which can be customized for mission specific
purposes, such as for the presentation of CellML models (through the
package cellml.pmr2_) and FieldML (fieldml.pmr2_).

.. _cellml.pmr2: https://github.com/PMR2/cellml.pmr2/
.. _fieldml.pmr2: https://github.com/PMR2/fieldml.pmr2/

PMR2 is the software behind the `Physiome Model Repository`_, which
currently hosts over 1000 CellML models and a handful of FieldML models
(and its precursor, exnode/exelem models).

.. _Physiome Model Repository: http://models.physiomeproject.org/


Features
========

Integration of Mercurial with Plone.

  - Can function as a standalone Mercurial repository with the ACL
    managed by Plone.  These are represented as a Workspace in PMR2.
  - Push/pull to the Mercurial instance managed by Plone using the same
    URI as is within the Plone instance.

Extensible presentational layer.

  - Presentation of data within the version control system in PMR2 are
    done using Exposures.  One may consider them wrappers around
    specific revisions around a Workspace, which provides a fixed point
    for users to process the model and/or data there to present them to
    other users.  The default only generators for RST and HTML.
  - Further views will have to be created as extensions to PMR2.  Please
    refer to cellml.pmr2 and fieldml.pmr2 for examples on how to extend
    PMR2 to suit your presentational needs.

All of PMR2 is fully extensible.

  - Even the storage layer can be extended.  Please refer to internal
    documentations.  At some point a GIT based storage library will be
    implemented.
  - This extensibility is based on zope.component and related
    libraries.

Please refer to the changelog for more details.


Installation
============

Please refer to pmr2.buildout_ for installation of this package, as the
correct installation procedure is tightly tied into buildout.

.. _pmr2.buildout: https://github.com/PMR2/pmr2.buildout/


Known issues and caveats
========================

To report PMR2 related issues, please use the `Physiome Tracker`_.

.. _Physiome Tracker: https://tracker.physiomeproject.org/

Other known minor caveats related to administration of PMR2:

- Some advanced Zope management knowledge may be required.
- Sometimes pushing doesn't work after installation.  This is due to
  the hgauthpas (The Mercurial credential authentication provider) not
  placed in the correct order.  From the ZMI, go to the acl_users under
  the Plone instance, plugins, Challenge Plugins, move hgauthpas to the
  top under Active Plugins.
